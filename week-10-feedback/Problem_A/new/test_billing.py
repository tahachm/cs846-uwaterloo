import os
import sys
import unittest

THIS_DIR = os.path.dirname(__file__)
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from billing_fixed import invoice_total_cents
from pricing_fixed import parse_price_to_cents


class TestBillingBehavior(unittest.TestCase):
    def test_parse_valid_prices(self) -> None:
        self.assertEqual(parse_price_to_cents("1.23"), 123)
        self.assertEqual(parse_price_to_cents("$2.00"), 200)
        self.assertEqual(parse_price_to_cents("2"), 200)
        self.assertEqual(parse_price_to_cents("2,000.50"), 200050)

    def test_invalid_prices_default_to_zero(self) -> None:
        self.assertEqual(parse_price_to_cents("FREE"), 0)
        self.assertEqual(parse_price_to_cents(""), 0)
        self.assertEqual(parse_price_to_cents(None), 0)
        self.assertEqual(parse_price_to_cents("-1.00"), 0)

    def test_invoice_total(self) -> None:
        self.assertEqual(invoice_total_cents(["1.00", "FREE", "2.00"]), 300)


if __name__ == "__main__":
    unittest.main()
