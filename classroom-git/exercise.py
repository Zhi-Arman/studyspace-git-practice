"""Standalone classroom tickets, unrelated to production booking rules."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ticket:
    description: str
    status: str = "new"
