"""Reservation rules and stable views shared by student and admin endpoints."""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.errors import fail
from app.models import Booking, OpeningException, Policy, Room, Seat, User
from app.security import audit, utcnow

SHANGHAI = ZoneInfo("Asia/Shanghai")


def iso(value: datetime | None) -> str | None:
    return value.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z") if value else None


def clock(value: int) -> str:
    return f"{value // 60:02d}:{value % 60:02d}"


def normalize_interval(
    db: Session, starts_at: datetime, ends_at: datetime, now: datetime | None = None
) -> tuple[datetime, datetime, date]:
    now = now or utcnow()
    start, end = starts_at.astimezone(SHANGHAI), ends_at.astimezone(SHANGHAI)
    start_utc = starts_at.astimezone(UTC).replace(tzinfo=None)
    end_utc = ends_at.astimezone(UTC).replace(tzinfo=None)
    if any(x.minute % 30 or x.second or x.microsecond for x in (start, end)):
        fail(422, "TIME_BOUNDARY", "Use exact half-hour boundaries.")
    if not timedelta(minutes=30) <= end_utc - start_utc <= timedelta(hours=24):
        fail(422, "TIME_RANGE", "Choose a duration between 30 minutes and 24 hours.")
    if end.date() != start.date() and not (
        end.date() == start.date() + timedelta(days=1) and end.hour == 0 and end.minute == 0
    ):
        fail(422, "TIME_RANGE", "A booking must stay within one business day.")
    if start_utc <= now:
        fail(422, "START_IN_PAST", "The start must be in the future.")
    today = now.replace(tzinfo=UTC).astimezone(SHANGHAI).date()
    days = db.get(Policy, 1).advance_days
    if not today <= start.date() < today + timedelta(days=days):
        fail(422, "BOOKING_WINDOW", "Choose a date inside the booking window.")
    return start_utc, end_utc, start.date()


def room_window(db: Session, room: Room, day: date) -> tuple[int, int] | None:
    exception = db.scalar(
        select(OpeningException).where(
            OpeningException.room_id == room.id, OpeningException.day == day
        )
    )
    if exception:
        return None if exception.closed else (exception.opens_at, exception.closes_at)
    return room.opens_at, room.closes_at


def fits_window(db: Session, room: Room, start: datetime, end: datetime, day: date) -> bool:
    window = room_window(db, room, day)
    if window is None:
        return False
    local_start = start.replace(tzinfo=UTC).astimezone(SHANGHAI)
    local_end = end.replace(tzinfo=UTC).astimezone(SHANGHAI)
    start_minutes = local_start.hour * 60 + local_start.minute
    end_minutes = 1440 if local_end.date() > day else local_end.hour * 60 + local_end.minute
    return window[0] <= start_minutes < end_minutes <= window[1]


def overlaps(start: datetime, end: datetime):
    return and_(Booking.cancelled_at.is_(None), Booking.starts_at < end, Booking.ends_at > start)


def room_view(db: Session, room: Room, day: date | None = None) -> dict:
    seats = db.scalars(select(Seat).where(Seat.room_id == room.id)).all()
    window = room_window(db, room, day) if day else (room.opens_at, room.closes_at)
    return {
        "id": room.id,
        "name": room.name,
        "campus": room.campus,
        "building": room.building,
        "floor": room.floor,
        "kind": room.kind,
        "description": room.description,
        "enabled": room.enabled,
        "capacity": sum(x.enabled for x in seats),
        "seat_count": len(seats),
        "opens_at": clock(window[0]) if window else None,
        "closes_at": clock(window[1]) if window else None,
        "closed": window is None,
        "regular_opens_at": clock(room.opens_at),
        "regular_closes_at": clock(room.closes_at),
    }


def booking_view(
    db: Session,
    booking: Booking,
    *,
    include_user: bool = False,
    actor: User | None = None,
    now: datetime | None = None,
) -> dict:
    now = now or utcnow()
    seat = db.get(Seat, booking.seat_id)
    room = db.get(Room, seat.room_id)
    status = (
        "CANCELLED"
        if booking.cancelled_at
        else "COMPLETED"
        if booking.ends_at <= now
        else "ONGOING"
        if booking.starts_at <= now
        else "UPCOMING"
    )
    value = {
        "id": booking.id,
        "seat_id": seat.id,
        "seat_code": seat.code,
        "room_id": room.id,
        "room_name": room.name,
        "business_date": booking.business_date.isoformat(),
        "starts_at": iso(booking.starts_at),
        "ends_at": iso(booking.ends_at),
        "created_at": iso(booking.created_at),
        "cancelled_at": iso(booking.cancelled_at),
        "cancellation_reason": booking.cancellation_reason,
        "status": status,
        "can_cancel": bool(
            actor
            and not booking.cancelled_at
            and booking.ends_at > now
            and (actor.role == "ADMIN" or (actor.id == booking.user_id and now < booking.starts_at))
        ),
    }
    if include_user:
        user = db.get(User, booking.user_id)
        value.update(
            {
                "user_id": user.id,
                "username": None if user.anonymized_at else user.username,
                "display_name": None if user.anonymized_at else user.display_name,
            }
        )
    return value


def cancel(db: Session, booking: Booking, actor_id: int, reason: str, now: datetime):
    if booking.cancelled_at:
        return
    booking.cancelled_at = now
    booking.cancelled_by = actor_id
    booking.cancellation_reason = reason
    audit(db, actor_id, "CANCEL_BOOKING", "booking", booking.id)


def reject_expired_history(day: date | None, now: datetime) -> None:
    if day and day < (now - timedelta(days=180)).replace(tzinfo=UTC).astimezone(SHANGHAI).date():
        fail(410, "HISTORY_EXPIRED", "This date is outside the retained history.")
