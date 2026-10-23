"""Admin operations keep eligibility changes and cancellation in the same lock."""

from datetime import UTC, date
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import AwareDatetime
from sqlalchemy import delete, func, select

from app.booking import (
    SHANGHAI,
    booking_view,
    cancel,
    fits_window,
    iso,
    reject_expired_history,
    room_view,
)
from app.database import DbSession, write_session
from app.errors import fail
from app.models import AuditEvent, Booking, LoginSession, OpeningException, Policy, Room, Seat, User
from app.reservations_api import Page, PageSize
from app.schemas import (
    CancelBooking,
    ExceptionInput,
    PolicyUpdate,
    RoomInput,
    SeatInput,
    UserUpdate,
    clock_minutes,
)
from app.security import audit, request_user, user_view, utcnow

router = APIRouter(prefix="/api/v1/admin", tags=["Local administration"])


def get_or_404(db, model, object_id):
    value = db.get(model, object_id)
    if value is None:
        fail(404, "NOT_FOUND", "Record not found.")
    return value


def reason_required(reason):
    if not reason:
        fail(422, "REASON_REQUIRED", "Provide a reason for this change.")


def cancel_affected(
    db, actor, reason, *, room_id=None, seat_id=None, user_id=None, check_window=False, day=None
):
    now = utcnow()
    query = (
        select(Booking)
        .join(Seat, Seat.id == Booking.seat_id)
        .where(Booking.cancelled_at.is_(None), Booking.ends_at > now)
    )
    if room_id is not None:
        query = query.where(Seat.room_id == room_id)
    if seat_id is not None:
        query = query.where(Booking.seat_id == seat_id)
    if user_id is not None:
        query = query.where(Booking.user_id == user_id)
    if day:
        query = query.where(Booking.business_date == day)
    count = 0
    for booking in db.scalars(query).all():
        seat = db.get(Seat, booking.seat_id)
        room = db.get(Room, seat.room_id)
        if not check_window or not fits_window(
            db, room, booking.starts_at, booking.ends_at, booking.business_date
        ):
            cancel(db, booking, actor.id, reason or "RESOURCE_CHANGED", now)
            count += 1
    return count


@router.get("/rooms")
def rooms(request: Request, db: DbSession):
    request_user(request, db, admin=True)
    values = db.scalars(select(Room).order_by(Room.id)).all()
    return {"items": [room_view(db, room) for room in values], "total": len(values)}


@router.post("/rooms", status_code=201)
def create_room(payload: RoomInput, request: Request):
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        values = payload.model_dump(exclude={"reason", "opens_at", "closes_at"})
        room = Room(
            **values,
            opens_at=clock_minutes(payload.opens_at),
            closes_at=clock_minutes(payload.closes_at, end=True),
        )
        db.add(room)
        db.flush()
        audit(db, actor.id, "CREATE_ROOM", "room", room.id)
        return room_view(db, room)


@router.put("/rooms/{room_id}")
def update_room(room_id: int, payload: RoomInput, request: Request):
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        room = get_or_404(db, Room, room_id)
        opening, closing = (
            clock_minutes(payload.opens_at),
            clock_minutes(payload.closes_at, end=True),
        )
        restricted = (
            (room.enabled and not payload.enabled)
            or opening > room.opens_at
            or closing < room.closes_at
        )
        if restricted:
            reason_required(payload.reason)
        for key, value in payload.model_dump(exclude={"reason", "opens_at", "closes_at"}).items():
            setattr(room, key, value)
        room.opens_at, room.closes_at = opening, closing
        db.flush()
        affected = cancel_affected(
            db, actor, payload.reason, room_id=room.id, check_window=room.enabled
        )
        audit(db, actor.id, "UPDATE_ROOM", "room", room.id)
        return {**room_view(db, room), "cancelled_bookings": affected}


@router.get("/rooms/{room_id}/seats")
def seats(room_id: int, request: Request, db: DbSession):
    request_user(request, db, admin=True)
    get_or_404(db, Room, room_id)
    rows = db.scalars(select(Seat).where(Seat.room_id == room_id).order_by(Seat.code)).all()
    return {
        "items": [
            {"id": x.id, "room_id": x.room_id, "code": x.code, "enabled": x.enabled} for x in rows
        ]
    }


@router.post("/seats", status_code=201)
def create_seat(payload: SeatInput, request: Request):
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        get_or_404(db, Room, payload.room_id)
        if db.scalar(
            select(Seat.id).where(Seat.room_id == payload.room_id, Seat.code == payload.code)
        ):
            fail(409, "SEAT_CODE_TAKEN", "Seat code already exists in this room.")
        seat = Seat(**payload.model_dump(exclude={"reason"}))
        db.add(seat)
        db.flush()
        audit(db, actor.id, "CREATE_SEAT", "seat", seat.id)
        return {"id": seat.id, "room_id": seat.room_id, "code": seat.code, "enabled": seat.enabled}


@router.put("/seats/{seat_id}")
def update_seat(seat_id: int, payload: SeatInput, request: Request):
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        seat = get_or_404(db, Seat, seat_id)
        if payload.room_id != seat.room_id:
            fail(409, "SEAT_ROOM_IMMUTABLE", "Create a new seat instead of moving an existing one.")
        if db.scalar(
            select(Seat.id).where(
                Seat.room_id == seat.room_id, Seat.code == payload.code, Seat.id != seat.id
            )
        ):
            fail(409, "SEAT_CODE_TAKEN", "Seat code already exists in this room.")
        if seat.enabled and not payload.enabled:
            reason_required(payload.reason)
        seat.code, seat.enabled = payload.code, payload.enabled
        affected = (
            cancel_affected(db, actor, payload.reason, seat_id=seat.id) if not seat.enabled else 0
        )
        audit(db, actor.id, "UPDATE_SEAT", "seat", seat.id)
        return {
            "id": seat.id,
            "room_id": seat.room_id,
            "code": seat.code,
            "enabled": seat.enabled,
            "cancelled_bookings": affected,
        }


@router.get("/opening-exceptions")
def opening_exceptions(request: Request, db: DbSession, room_id: int | None = None):
    request_user(request, db, admin=True)
    query = select(OpeningException)
    if room_id is not None:
        query = query.where(OpeningException.room_id == room_id)
    from app.booking import clock

    rows = db.scalars(query.order_by(OpeningException.day.desc())).all()
    return {
        "items": [
            {
                "id": row.id,
                "room_id": row.room_id,
                "day": row.day.isoformat(),
                "closed": row.closed,
                "opens_at": clock(row.opens_at),
                "closes_at": clock(row.closes_at),
            }
            for row in rows
        ]
    }


@router.post("/opening-exceptions", status_code=201)
def set_exception(payload: ExceptionInput, request: Request):
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        room = get_or_404(db, Room, payload.room_id)
        exception = db.scalar(
            select(OpeningException).where(
                OpeningException.room_id == room.id, OpeningException.day == payload.day
            )
        )
        if exception is None:
            exception = OpeningException(room_id=room.id, day=payload.day)
            db.add(exception)
        exception.closed = payload.closed
        exception.opens_at = clock_minutes(payload.opens_at)
        exception.closes_at = clock_minutes(payload.closes_at, end=True)
        db.flush()
        affected = cancel_affected(
            db, actor, payload.reason, room_id=room.id, check_window=True, day=payload.day
        )
        audit(db, actor.id, "SET_OPENING_EXCEPTION", "room", room.id)
        return {"id": exception.id, "cancelled_bookings": affected}


@router.post("/opening-exceptions/{exception_id}/remove")
def remove_exception(exception_id: int, payload: CancelBooking, request: Request):
    reason_required(payload.reason)
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        exception = get_or_404(db, OpeningException, exception_id)
        room_id, day = exception.room_id, exception.day
        db.delete(exception)
        db.flush()
        affected = cancel_affected(
            db, actor, payload.reason, room_id=room_id, check_window=True, day=day
        )
        audit(db, actor.id, "REMOVE_OPENING_EXCEPTION", "room", room_id)
        return {"cancelled_bookings": affected}


@router.put("/policy")
def update_policy(payload: PolicyUpdate, request: Request):
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        policy = db.get(Policy, 1)
        policy.advance_days = payload.advance_days
        audit(db, actor.id, "UPDATE_POLICY", "policy", 1)
        return {"advance_days": policy.advance_days}


@router.get("/users")
def users(
    request: Request, db: DbSession, q: str | None = None, page: Page = 1, page_size: PageSize = 20
):
    request_user(request, db, admin=True)
    query = select(User)
    if q:
        query = query.where(User.username.icontains(q, autoescape=True))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(query.order_by(User.id).offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [user_view(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate, request: Request):
    with write_session(request) as db:
        actor = request_user(request, db, admin=True)
        user = get_or_404(db, User, user_id)
        if user.anonymized_at:
            fail(409, "USER_ANONYMIZED", "An anonymized account cannot be reactivated.")
        if (
            user.role == "ADMIN"
            and user.enabled
            and (payload.role != "ADMIN" or not payload.enabled)
        ):
            count = db.scalar(
                select(func.count())
                .select_from(User)
                .where(User.role == "ADMIN", User.enabled.is_(True))
            )
            if count <= 1:
                fail(409, "LAST_ADMIN", "At least one enabled administrator must remain.")
        revoke = user.enabled != payload.enabled or user.role != payload.role
        user.enabled, user.role = payload.enabled, payload.role
        user.disabled_at = (user.disabled_at or utcnow()) if not payload.enabled else None
        affected = 0
        if revoke:
            db.execute(delete(LoginSession).where(LoginSession.user_id == user.id))
            if not user.enabled or user.role != "STUDENT":
                affected = cancel_affected(db, actor, payload.reason, user_id=user.id)
        audit(db, actor.id, "UPDATE_USER", "user", user.id)
        return {**user_view(user), "cancelled_bookings": affected}


@router.get("/bookings")
def bookings(
    request: Request,
    db: DbSession,
    day: date | None = None,
    room_id: int | None = None,
    seat_id: int | None = None,
    username: str | None = None,
    status: Literal["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"] | None = None,
    page: Page = 1,
    page_size: PageSize = 20,
):
    actor = request_user(request, db, admin=True)
    now = utcnow()
    reject_expired_history(day, now)
    query = (
        select(Booking)
        .join(Seat, Booking.seat_id == Seat.id)
        .join(User, Booking.user_id == User.id)
    )
    if day:
        query = query.where(Booking.business_date == day)
    if room_id is not None:
        query = query.where(Seat.room_id == room_id)
    if seat_id is not None:
        query = query.where(Seat.id == seat_id)
    if username:
        query = query.where(User.username.icontains(username, autoescape=True))
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
        "items": [booking_view(db, row, include_user=True, actor=actor, now=now) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/statistics")
def statistics(
    request: Request, db: DbSession, day: date | None = None, as_of: AwareDatetime | None = None
):
    request_user(request, db, admin=True)
    now = utcnow()
    snapshot = as_of.astimezone(UTC).replace(tzinfo=None) if as_of else now
    if snapshot > now:
        fail(422, "FUTURE_SNAPSHOT", "The statistics snapshot cannot be in the future.")
    day = day or now.replace(tzinfo=UTC).astimezone(SHANGHAI).date()
    reject_expired_history(day, now)
    rows = db.scalars(
        select(Booking).where(Booking.business_date == day, Booking.created_at <= snapshot)
    ).all()
    return {
        "day": day.isoformat(),
        "as_of": iso(snapshot),
        "created": len(rows),
        "cancelled": sum(bool(x.cancelled_at and x.cancelled_at <= snapshot) for x in rows),
        "active": sum(
            x.ends_at > snapshot and (x.cancelled_at is None or x.cancelled_at > snapshot)
            for x in rows
        ),
    }


@router.get("/audit")
def events(request: Request, db: DbSession, page: Page = 1, page_size: PageSize = 20):
    request_user(request, db, admin=True)
    rows = db.scalars(
        select(AuditEvent)
        .order_by(AuditEvent.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    total = db.scalar(select(func.count()).select_from(AuditEvent))
    return {
        "items": [
            {
                "id": x.id,
                "actor_id": x.actor_id,
                "action": x.action,
                "target_type": x.target_type,
                "target_id": x.target_id,
                "created_at": iso(x.created_at),
            }
            for x in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
