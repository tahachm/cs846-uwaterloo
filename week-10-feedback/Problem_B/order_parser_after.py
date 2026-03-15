from dataclasses import dataclass


class OrderParseError(Exception):
    pass


@dataclass
class ParsedOrder:
    order_id: int
    amount_cents: int
    customer_email: str


def parse_order(payload: dict) -> ParsedOrder | None:
    """
    Parse and validate an incoming order payload.
    Returns None if parsing fails.
    """

    try:
        order_id = int(payload.get("order_id"))
        amount_cents = int(payload.get("amount_cents"))
        customer_email = payload.get("customer_email", "").strip()

        if amount_cents < 0:
            return None
        if "@" not in customer_email:
            return None

        return ParsedOrder(
            order_id=order_id,
            amount_cents=amount_cents,
            customer_email=customer_email,
        )
    except Exception:
        return None