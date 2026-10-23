"""Standalone classroom tickets, unrelated to production booking rules."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ticket:
    description: str
    status: str = "new"


def validate_description(value: str) -> str:
    """Return stripped text containing 10 through 500 Unicode code points."""
    if not isinstance(value, str):
        raise TypeError("description must be a string")
    normalized = value.strip()
    if not 10 <= len(normalized) <= 500:
        raise ValueError("description must contain 10 to 500 characters")
    return normalized
