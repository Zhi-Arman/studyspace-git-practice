"""Standalone classroom tickets, unrelated to production booking rules."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ticket:
    description: str
    status: str = "new"


TRANSITIONS = {
    "new": frozenset({"in_progress"}),
    "in_progress": frozenset({"resolved"}),
    "resolved": frozenset({"in_progress", "closed"}),
    "closed": frozenset(),
}


def transition_ticket(ticket: Ticket, target: str) -> Ticket:
    """Return a new ticket for an allowed transition, preserving the input."""
    from dataclasses import replace

    if not isinstance(ticket, Ticket):
        raise TypeError("ticket must be a Ticket")
    if not isinstance(target, str):
        raise TypeError("target status must be a string")
    if ticket.status not in TRANSITIONS or target not in TRANSITIONS:
        raise ValueError("unknown status")
    if target not in TRANSITIONS[ticket.status]:
        raise ValueError("transition is not allowed")
    return replace(ticket, status=target)
