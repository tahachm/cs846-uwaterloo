from dataclasses import dataclass


class OrderParseError(Exception):
    pass


@dataclass
class ParsedOrder:
    order_id: int
    amount_cents: int
    customer_email: str


def parse_order(payload: dict) -> ParsedOrder:
    """
    Parse and validate an incoming order payload.

    Contract:
    - order_id is required and must be an integer-like value
    - amount_cents is required and must be a non-negative integer
    - customer_email is required and must contain '@'
    - invalid payloads must raise OrderParseError
    """

    if "order_id" not in payload:
        raise OrderParseError("missing order_id")
    if "amount_cents" not in payload:
        raise OrderParseError("missing amount_cents")
    if "customer_email" not in payload:
        raise OrderParseError("missing customer_email")

    try:
        order_id = int(payload["order_id"])
    except (TypeError, ValueError):
        raise OrderParseError("invalid order_id")

    try:
        amount_cents = int(payload["amount_cents"])
    except (TypeError, ValueError):
        raise OrderParseError("invalid amount_cents")

    if amount_cents < 0:
        raise OrderParseError("amount_cents must be non-negative")

    customer_email = payload["customer_email"]
    if not isinstance(customer_email, str) or "@" not in customer_email:
        raise OrderParseError("invalid customer_email")

    return ParsedOrder(
        order_id=order_id,
        amount_cents=amount_cents,
        customer_email=customer_email,
    )