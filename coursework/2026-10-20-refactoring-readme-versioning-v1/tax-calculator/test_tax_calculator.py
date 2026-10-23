"""Tests for the behavior documented in the example README."""

import unittest
from decimal import Decimal

from tax_calculator import calculate_tax


class TaxCalculatorTests(unittest.TestCase):
    def test_percentage_example(self):
        self.assertEqual(calculate_tax(Decimal("10000"), Decimal("13")), Decimal("1300.00"))

    def test_zero_amount_and_rate(self):
        self.assertEqual(calculate_tax(Decimal("0"), Decimal("13")), Decimal("0.00"))
        self.assertEqual(calculate_tax(Decimal("100"), Decimal("0")), Decimal("0.00"))

    def test_half_cent_rounds_up(self):
        self.assertEqual(calculate_tax(Decimal("0.05"), Decimal("10")), Decimal("0.01"))

    def test_invalid_inputs(self):
        for amount, rate in [("-1", "13"), ("100", "-1"), ("100", "101"), ("NaN", "13"), ("100", "Infinity")]:
            with self.subTest(amount=amount, rate=rate):
                with self.assertRaises(ValueError):
                    calculate_tax(Decimal(amount), Decimal(rate))


if __name__ == "__main__":
    unittest.main()
