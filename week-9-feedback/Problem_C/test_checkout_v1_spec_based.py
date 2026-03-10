"""
Generated tests for CheckoutService.process_checkout — V1 (spec-based).

Prompt used (Guideline 1):
    "Generate pytest unit tests for CheckoutService.process_checkout.
     Framework: pytest + unittest.mock.MagicMock for InventoryService and PaymentGateway.
     Cover each rule per the specification:
       - Stock check: error when out of stock, success when in stock
       - Flash-sale discount (5%), bundle discount (quantity >= 3, 5%)
       - SAVE10 (10%, min $100), SUMMER20 (20% capped at $30, min $75)
       - VIP discount (15%) incompatible with SAVE10/SUMMER20; FLASH5 incompatible with VIP
       - Loyalty credit applied only when points >= 500
       - Shipping: $10 if discounted subtotal < $50, else $0
       - Tax: 13% on post-discount, post-loyalty-credit amount
       - Payment failure -> CheckoutError
       - Total must never be negative"
"""

import pytest
from unittest.mock import MagicMock

from checkout_service import (
    CartItem, Cart, Customer, CustomerTier,
    CheckoutService, CheckoutError,
    InventoryService, PaymentGateway,
)


# ── fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def service():
    inventory = MagicMock(spec=InventoryService)
    payment = MagicMock(spec=PaymentGateway)
    inventory.check_stock.return_value = True   # in stock by default
    payment.charge.return_value = {"success": True}
    return CheckoutService(inventory, payment)


def _cart(*items):
    c = Cart()
    for item in items:
        c.add_item(item)
    return c


def _regular(points=0):
    return Customer("c1", "Alice", CustomerTier.REGULAR, loyalty_points=points)


def _vip(points=0):
    return Customer("c2", "Bob", CustomerTier.VIP, loyalty_points=points)


# ── 1. Stock validation ──────────────────────────────────────────────

def test_in_stock_succeeds(service):
    """Item in stock → checkout should succeed."""
    cart = _cart(CartItem("p1", "Widget", 25.0, 2))
    result = service.process_checkout(cart, _regular())
    assert result["status"] == "success"


def test_out_of_stock_raises(service):
    """Item NOT in stock → CheckoutError."""
    service.inventory.check_stock.return_value = False
    cart = _cart(CartItem("p1", "Widget", 25.0, 2))
    with pytest.raises(CheckoutError, match="out of stock"):
        service.process_checkout(cart, _regular())


# ── 2. Bundle discount boundary (quantity >= 3) ─────────────────────

@pytest.mark.parametrize("qty, expect_bundle", [
    (2, False),
    (3, True),   # boundary: exactly 3 should get bundle
    (4, True),
])
def test_bundle_discount_boundary(service, qty, expect_bundle):
    price = 20.0
    cart = _cart(CartItem("p1", "Widget", price, qty))
    result = service.process_checkout(cart, _regular())
    if expect_bundle:
        # 5% flash-sale not active, 5% bundle → unit = 20 * 0.95
        expected_subtotal = price * 0.95 * qty
    else:
        expected_subtotal = price * qty
    assert result["subtotal"] == pytest.approx(expected_subtotal, abs=0.01)


# ── 3. SUMMER20 coupon cap ───────────────────────────────────────────

def test_summer20_discount_is_capped_at_30(service):
    """SUMMER20 gives 20% but capped at $30 max discount."""
    # subtotal = $200 → 20% = $40 → should be capped to $30
    cart = _cart(CartItem("p1", "Widget", 100.0, 2))
    result = service.process_checkout(cart, _regular(), coupon_code="SUMMER20")
    assert result["discount"] == pytest.approx(30.0, abs=0.01)


# ── 4. Tax on post-discount amount ──────────────────────────────────

def test_tax_calculated_on_discounted_subtotal(service):
    """Tax (13%) should be applied AFTER discounts, per spec."""
    # subtotal = $200, SAVE10 discount = $20, discounted = $180
    cart = _cart(CartItem("p1", "Widget", 100.0, 2))
    result = service.process_checkout(cart, _regular(), coupon_code="SAVE10")
    discounted = 200.0 - 20.0  # $180
    expected_tax = discounted * 0.13  # $23.40
    assert result["tax"] == pytest.approx(expected_tax, abs=0.01)


# ── 5. Shipping on discounted subtotal ───────────────────────────────

def test_shipping_uses_discounted_subtotal(service):
    """Shipping should be free when DISCOUNTED subtotal >= $50."""
    # subtotal = $55, SAVE10 requires $100 min so use no coupon
    # VIP discount 15% → discounted = 55 * 0.85 = 46.75 < 50 → $10 shipping
    cart = _cart(CartItem("p1", "Widget", 55.0, 1))
    result = service.process_checkout(cart, _vip())
    # discounted_subtotal = 55 - 8.25 = 46.75 → should charge shipping
    assert result["shipping"] == pytest.approx(10.0, abs=0.01)


def test_shipping_free_when_discounted_above_50(service):
    """Shipping free when discounted subtotal >= $50."""
    # subtotal = $60, no coupon, regular customer → discounted = $60 >= 50 → free
    cart = _cart(CartItem("p1", "Widget", 60.0, 1))
    result = service.process_checkout(cart, _regular())
    assert result["shipping"] == pytest.approx(0.0, abs=0.01)


# ── 6. FLASH5 + VIP incompatibility ─────────────────────────────────

def test_flash5_incompatible_with_vip(service):
    """Per spec, FLASH5 should not be combinable with VIP discount."""
    cart = _cart(CartItem("p1", "Widget", 50.0, 2, flash_sale=True))
    with pytest.raises(CheckoutError):
        service.process_checkout(cart, _vip(), coupon_code="FLASH5")
