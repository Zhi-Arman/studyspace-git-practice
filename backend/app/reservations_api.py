"""Public resources and authenticated single-seat reservations."""

from datetime import UTC, date, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Query, Request
from pydantic import AwareDatetime
from sqlalchemy import func, select

from app.booking import (
    SHANGHAI,
    booking_view,
    cancel,
    fits_window,
    normalize_interval,
    overlaps,
    reject_expired_history,
    room_view,
)
from app.database import DbSession, write_session
from app.errors import fail
from app.models import Booking, Policy, Room, Seat
from app.schemas import CancelBooking, CreateBooking
from app.security import audit, request_user, utcnow

router = APIRouter(prefix="/api/v1", tags=["Reservations"])
Page = Annotated[int, Query(ge=1)]
PageSize = Annotated[int, Query(ge=1, le=100)]


@router.get("/policy")
def policy(db: DbSession):
    return {
        "timezone": "Asia/Shanghai",
        "today": utcnow().replace(tzinfo=UTC).astimezone(SHANGHAI).date().isoformat(),
        "advance_days": db.get(Policy, 1).advance_days,
        "granularity_minutes": 30,
        "max_duration_hours": 24,
        "identity_mode": "LOCAL_ONLY",
    }


@router.get("/rooms")
def rooms(
    db: DbSession,
    campus: str | None = None,
    building: str | None = None,
    floor: int | None = None,
    kind: Literal["CLASSROOM", "STUDY_ROOM"] | None = None,
    day: date | None = None,
    page: Page = 1,
    page_size: PageSize = 20,
):
    query = select(Room).where(Room.enabled.is_(True))
    if campus:
        query = query.where(Room.campus.icontains(campus, autoescape=True))
    if building:
        query = query.where(Room.building.icontains(building, autoescape=True))
    if floor is not None:
        query = query.where(Room.floor == floor)
    if kind:
        query = query.where(Room.kind == kind)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(query.order_by(Room.id).offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [room_view(db, row, day) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/rooms/{room_id}/seats")
def seats(room_id: int, starts_at: AwareDatetime, ends_at: AwareDatetime, db: DbSession):
    room = db.get(Room, room_id)
    if room is None or not room.enabled:
        fail(404, "ROOM_NOT_FOUND", "Room not found.")
    start, end, day = normalize_interval(db, starts_at, ends_at)
    opened = fits_window(db, room, start, end, day)
    occupied = set(db.scalars(select(Booking.seat_id).where(overlaps(start, end))).all())
    rows = db.scalars(select(Seat).where(Seat.room_id == room.id).order_by(Seat.code)).all()
    return {
        "room": room_view(db, room, day),
        "items": [
            {
                "id": row.id,
                "room_id": row.room_id,
                "code": row.code,
                "enabled": row.enabled,
                "available": bool(row.enabled and opened and row.id not in occupied),
            }
            for row in rows
        ],
    }


@router.post("/bookings", status_code=201)
def create_booking(payload: CreateBooking, request: Request):
    with write_session(request) as db:
        user = request_user(request, db)
        if user.role != "STUDENT":
            fail(403, "STUDENT_REQUIRED", "Use a student account to book a seat.")
        now = utcnow()  # The lock is already held.
        start, end, day = normalize_interval(db, payload.starts_at, payload.ends_at, now)
        seat = db.get(Seat, payload.seat_id)
        if seat is None:
            fail(404, "SEAT_NOT_FOUND", "Seat not found.")
        room = db.get(Room, seat.room_id)
        if not seat.enabled or not room.enabled:
            fail(409, "RESOURCE_DISABLED", "This resource is disabled.")
        if not fits_window(db, room, start, end, day):
            fail(422, "OUTSIDE_OPENING", "The interval is outside opening hours.")
        if db.scalar(
            select(Booking.id).where(Booking.user_id == user.id, overlaps(start, end)).limit(1)
        ):
            fail(409, "USER_CONFLICT", "You already have a booking during this interval.")
        if db.scalar(
            select(Booking.id).where(Booking.seat_id == seat.id, overlaps(start, end)).limit(1)
        ):
            fail(409, "SEAT_CONFLICT", "This seat was just reserved. Choose another.")
        booking = Booking(
            user_id=user.id,
            seat_id=seat.id,
            business_date=day,
            starts_at=start,
            ends_at=end,
            created_at=now,
        )
        db.add(booking)
        db.flush()
        audit(db, user.id, "CREATE_BOOKING", "booking", booking.id)
        return booking_view(db, booking, actor=user, now=now)


@router.get("/bookings")
def my_bookings(
    request: Request,
    db: DbSession,
    day: date | None = None,
    status: Literal["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"] | None = None,
    page: Page = 1,
    page_size: PageSize = 20,
):
    user = request_user(request, db)
    now = utcnow()
    reject_expired_history(day, now)
    query = select(Booking).where(Booking.user_id == user.id)
    if day:
        query = query.where(Booking.business_date == day)
    if status == "CANCELLED":
        query = query.where(Booking.cancelled_at.is_not(None))
    elif status:
        query = query.where(Booking.cancelled_at.is_(None))
        if status == "UPCOMING":
            query = query.where(Booking.starts_at > now)
        elif status == "ONGOING":
            query = query.where(Booking.starts_at <= now, Booking.ends_at > now)
        else:
            query = query.where(Booking.ends_at <= now)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(
        query.order_by(Booking.starts_at.desc(), Booking.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "items": [booking_view(db, row, actor=user, now=now) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "history_from": (now - timedelta(days=180)).date().isoformat(),
    }


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, payload: CancelBooking, request: Request):
    with write_session(request) as db:
        user = request_user(request, db)
        booking = db.get(Booking, booking_id)
        if booking is None or (user.role != "ADMIN" and booking.user_id != user.id):
            fail(404, "BOOKING_NOT_FOUND", "Booking not found.")
        if not booking.cancelled_at:
            now = utcnow()
            if booking.ends_at <= now:
                fail(409, "BOOKING_COMPLETED", "A completed booking cannot be cancelled.")
            if user.role == "ADMIN":
                if not payload.reason:
                    fail(422, "REASON_REQUIRED", "An administrator must provide a reason.")
            elif now >= booking.starts_at:
                fail(409, "CANCEL_TOO_LATE", "This booking has started. Ask an administrator.")
            cancel(db, booking, user.id, payload.reason or "STUDENT_CANCELLED", now)
        return booking_view(db, booking, actor=user)
