from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class InvalidPriceError(ValueError):
    """Raised when a user-supplied price cannot be parsed safely."""


def parse_price_to_cents(text: str | None) -> int:
    """Parse a user-supplied price string into integer cents."""

    if text is None:
        return 0

    cleaned = text.strip()
    if cleaned == "":
        return 0

    cleaned = cleaned.replace("$", "").replace(",", "")

    try:
        amount = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return 0

    cents = int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    if cents < 0:
        return 0

    return cents
