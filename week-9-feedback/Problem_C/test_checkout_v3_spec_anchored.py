"""
Spec-anchored tests for CheckoutService.process_checkout — V3.

Produced by the UPDATED Guideline 2 (spec-anchored repair loop):
    "Running the tests produced 9 failures. For each failure, compare the
     test's expected value against the ORIGINAL SPECIFICATION (docstrings,
     comments, prompt requirements). Classify each failure as:
       (A) TEST BUG  — the test contradicts the spec, fix the test.
       (B) IMPL BUG  — the test matches the spec but the code disagrees.
           Mark with # IMPL_BUG and keep the spec-correct assertion, but
           xfail so the suite is runnable.
       (C) UNCLEAR   — spec is ambiguous, flag for human review.
     Do not modify checkout_service.py."

Result: The LLM correctly identifies 6 implementation bugs and 0 test bugs
when anchored to the spec. The stock-check inversion is fixed in the mock
(since the InventoryService docstring says True = available), and the
remaining spec violations are preserved as xfail markers.
"""

import pytest
from unittest.mock import MagicMock

from checkout_service import (
    CartItem, Cart, Customer, CustomerTier,
    CheckoutService, CheckoutError,
    InventoryService, PaymentGateway,
)


@pytest.fixture
def service():
    inventory = MagicMock(spec=InventoryService)
    payment = MagicMock(spec=PaymentGateway)
    # InventoryService docstring: "Returns True if available"
    # But code raises on True → this is IMPL BUG #1 (inverted stock check).
    # We mock False so other tests can run, but we test the inversion below.
    inventory.check_stock.return_value = False
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


# ── IMPL BUG #1: Stock check is inverted ─────────────────────────────
# InventoryService.check_stock docstring says "Returns True if available".
# Code raises CheckoutError when check_stock returns True — inverted logic.

@pytest.mark.xfail(reason="IMPL BUG: stock check inverted — raises on True (available)")
def test_in_stock_should_succeed_with_true(service):
    service.inventory.check_stock.return_value = True  # True = available per docstring
    cart = _cart(CartItem("p1", "Widget", 25.0, 2))
    result = service.process_checkout(cart, _regular())
    assert result["status"] == "success"


@pytest.mark.xfail(reason="IMPL BUG: stock check inverted — does not raise on False")
def test_out_of_stock_should_raise_with_false(service):
    service.inventory.check_stock.return_value = False  # False = unavailable per docstring
    cart = _cart(CartItem("p1", "Widget", 25.0, 2))
    with pytest.raises(CheckoutError, match="out of stock"):
        service.process_checkout(cart, _regular())


# ── IMPL BUG #2: Bundle threshold uses > instead of >= ───────────────
# Spec says "bundle discount (quantity >= 3, 5%)" but code uses > 3.

@pytest.mark.xfail(reason="IMPL BUG: bundle uses > instead of >=, qty=3 gets no discount")
def test_bundle_discount_at_exactly_3(service):
    cart = _cart(CartItem("p1", "Widget", 20.0, 3))
    result = service.process_checkout(cart, _regular())
    expected = 20.0 * 0.95 * 3  # $57.00 with bundle
    assert result["subtotal"] == pytest.approx(expected, abs=0.01)


def test_bundle_discount_at_4(service):
    cart = _cart(CartItem("p1", "Widget", 20.0, 4))
    result = service.process_checkout(cart, _regular())
    expected = 20.0 * 0.95 * 4
    assert result["subtotal"] == pytest.approx(expected, abs=0.01)


# ── IMPL BUG #3: SUMMER20 uses max() instead of min() ────────────────
# Spec says "20% capped at $30" → min(raw, 30). Code uses max(raw, 30).

@pytest.mark.xfail(reason="IMPL BUG: SUMMER20 uses max() not min() — discount exceeds cap")
def test_summer20_capped_at_30(service):
    cart = _cart(CartItem("p1", "Widget", 100.0, 2))  # subtotal=$200
    result = service.process_checkout(cart, _regular(), coupon_code="SUMMER20")
    assert result["discount"] == pytest.approx(30.0, abs=0.01)  # spec says cap at $30


# ── IMPL BUG #4: Tax on subtotal instead of discounted amount ────────
# Spec says "Tax: 13% on post-discount, post-loyalty-credit amount".
# Code computes tax = subtotal * 0.13 (before discount).

@pytest.mark.xfail(reason="IMPL BUG: tax computed on subtotal, not discounted amount")
def test_tax_on_discounted_amount(service):
    cart = _cart(CartItem("p1", "Widget", 100.0, 2))  # subtotal=$200
    result = service.process_checkout(cart, _regular(), coupon_code="SAVE10")
    discounted = 200.0 - 20.0  # $180
    expected_tax = discounted * 0.13  # $23.40
    assert result["tax"] == pytest.approx(expected_tax, abs=0.01)


# ── IMPL BUG #5: Shipping checks subtotal, not discounted_subtotal ───
# Spec says "Shipping: $10 if discounted subtotal < $50, else $0".
# Code checks `subtotal` (pre-discount) instead of `discounted_subtotal`.

@pytest.mark.xfail(reason="IMPL BUG: shipping checks subtotal, not discounted_subtotal")
def test_shipping_on_discounted_subtotal(service):
    # subtotal=$55, VIP 15% discount → discounted=$46.75 < $50 → should charge $10
    cart = _cart(CartItem("p1", "Widget", 55.0, 1))
    result = service.process_checkout(cart, _vip())
    assert result["shipping"] == pytest.approx(10.0, abs=0.01)


# ── IMPL BUG #6: FLASH5 not checked for VIP incompatibility ──────────
# Spec says "FLASH5 incompatible with VIP". Code has no such check.

@pytest.mark.xfail(reason="IMPL BUG: FLASH5+VIP incompatibility not enforced")
def test_flash5_incompatible_with_vip(service):
    cart = _cart(CartItem("p1", "Widget", 50.0, 2, flash_sale=True))
    with pytest.raises(CheckoutError):
        service.process_checkout(cart, _vip(), coupon_code="FLASH5")


# ── Tests that pass correctly (no bugs in these paths) ────────────────

def test_save10_applied_correctly(service):
    cart = _cart(CartItem("p1", "Widget", 100.0, 2))  # subtotal=$200
    result = service.process_checkout(cart, _regular(), coupon_code="SAVE10")
    assert result["discount"] == pytest.approx(20.0, abs=0.01)
    assert result["coupon_applied"] == "SAVE10"


def test_vip_discount(service):
    cart = _cart(CartItem("p1", "Widget", 50.0, 2))  # subtotal=$100
    result = service.process_checkout(cart, _vip())
    assert result["discount"] == pytest.approx(15.0, abs=0.01)


def test_loyalty_points_redeemed(service):
    cart = _cart(CartItem("p1", "Widget", 50.0, 2))
    customer = _regular(points=600)
    result = service.process_checkout(cart, customer, redeem_points=True)
    assert result["points_redeemed"] == 100
