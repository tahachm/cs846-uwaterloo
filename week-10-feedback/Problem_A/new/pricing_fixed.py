from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class InvalidPriceError(ValueError):
    """Raised when a user-supplied price cannot be parsed safely."""


def parse_price_to_cents(text: str | None) -> int:
    """Parse a user-supplied price string into integer cents.
    """

    if text is None:
        raise InvalidPriceError("price is required")

    cleaned = text.strip()
    if cleaned == "":
        raise InvalidPriceError("price is required")

    cleaned = cleaned.replace("$", "").replace(",", "")

    try:
        amount = Decimal(cleaned)
    except (InvalidOperation, ValueError) as exc:
        raise InvalidPriceError(f"invalid price: {text!r}") from exc

    cents = int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    if cents < 0:
        raise InvalidPriceError("price must be non-negative")

    return cents
