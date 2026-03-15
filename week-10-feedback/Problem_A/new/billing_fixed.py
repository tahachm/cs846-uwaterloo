from __future__ import annotations

from pricing_fixed import parse_price_to_cents


def invoice_total_cents(line_item_prices: list[str | None]) -> int:
    """Sum a list of user-entered prices."""

    return sum(parse_price_to_cents(p) for p in line_item_prices)
