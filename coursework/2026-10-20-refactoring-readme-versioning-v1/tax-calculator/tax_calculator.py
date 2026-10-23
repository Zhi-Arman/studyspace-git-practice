"""A classroom percentage calculator; rates are supplied by the user."""

import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def calculate_tax(amount: Decimal, rate: Decimal) -> Decimal:
    """Return amount * rate / 100, rounded to cents with ROUND_HALF_UP.

    Require a finite, non-negative amount and a finite rate from 0 to 100.
    """
    if not amount.is_finite() or amount < 0:
        raise ValueError("amount must be finite and non-negative")
    if not rate.is_finite() or not Decimal("0") <= rate <= Decimal("100"):
        raise ValueError("rate must be between 0 and 100")
    try:
        return (amount * rate / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except InvalidOperation as error:
        raise ValueError("amount exceeds supported decimal precision") from error


def main() -> None:
    """Read decimal arguments and print the calculated tax amount."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--amount", required=True, help="non-negative decimal amount")
    parser.add_argument("--rate", required=True, help="percentage from 0 to 100")
    args = parser.parse_args()
    try:
        tax = calculate_tax(Decimal(args.amount), Decimal(args.rate))
    except (InvalidOperation, ValueError) as error:
        parser.error(str(error) or "use decimal numbers with a decimal point")
    print(f"Tax: {tax:.2f}")


if __name__ == "__main__":
    main()
