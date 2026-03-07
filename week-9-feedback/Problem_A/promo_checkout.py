from dataclasses import dataclass
from typing import List, Optional


class CheckoutError(Exception):
    pass


@dataclass
class Item:
    name: str
    price: float
    quantity: int
    flash_sale: bool = False


@dataclass
class CheckoutResult:
    subtotal: float
    discount: float
    shipping: float
    tax: float
    total: float
    charged: bool


class PaymentGateway:
    def charge(self, amount: float) -> bool:
        return amount >= 0


def process_checkout(
    items: List[Item],
    coupon_code: Optional[str],
    is_vip: bool,
    payment_gateway: PaymentGateway,
) -> CheckoutResult:
 

    if items is None:
        raise CheckoutError("items is required")
    if payment_gateway is None:
        raise CheckoutError("payment gateway is required")

    subtotal = 0.0
    for item in items:
        if item.quantity <= 0:
            raise CheckoutError("quantity must be positive")
        if item.price < 0:
            raise CheckoutError("price cannot be negative")
        subtotal += item.price * item.quantity

    discount = 0.0

    # item-level discounts
    for item in items:
        line_total = item.price * item.quantity
        if item.flash_sale:
            discount += line_total * 0.05
        if item.quantity >= 3:
            discount += line_total * 0.05

    # VIP discount
    if is_vip:
        discount += subtotal * 0.10

    # coupon discounts
    if coupon_code:
        if coupon_code == "SAVE10":
            if subtotal >= 50:
                discount += subtotal * 0.10
        elif coupon_code == "FREESHIP":
            pass
        else:
            raise CheckoutError("invalid coupon code")

    discounted_subtotal = subtotal - discount

   
    if subtotal == 0:
        shipping = 0.0
    elif coupon_code == "FREESHIP":
        shipping = 0.0
    elif subtotal >= 50:
        shipping = 0.0
    else:
        shipping = 10.0

    tax = discounted_subtotal * 0.13
    total = discounted_subtotal + shipping + tax

    charged = payment_gateway.charge(total)
    if not charged:
        raise CheckoutError("payment failed")

    return CheckoutResult(
        subtotal=round(subtotal, 2),
        discount=round(discount, 2),
        shipping=round(shipping, 2),
        tax=round(tax, 2),
        total=round(total, 2),
        charged=charged,
    )