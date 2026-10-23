"""Real SQLite integration, including separate concurrent request connections."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Room, Seat
from tests.test_local_accounts import WRITE, login, register


@pytest.fixture
def resources(engine, client):
    with Session(engine) as db:
        room = Room(
            name="演示自习室",
            campus="Demo",
            building="Library",
            floor=2,
            kind="STUDY_ROOM",
            description="Synthetic resources",
            enabled=True,
            opens_at=480,
            closes_at=1320,
        )
        db.add(room)
        db.flush()
        seats = [Seat(room_id=room.id, code=code, enabled=True) for code in ["A01", "A02"]]
        db.add_all(seats)
        db.commit()
        return {"room": room.id, "seats": [x.id for x in seats]}


def interval(start="09:00", end="10:00", days=1):
    day = (datetime.now(ZoneInfo("Asia/Shanghai")) + timedelta(days=days)).date().isoformat()
    return {"starts_at": f"{day}T{start}:00+08:00", "ends_at": f"{day}T{end}:00+08:00"}


def book(client, seat_id, **times):
    return client.post(
        "/api/v1/bookings", json={"seat_id": seat_id, **(times or interval())}, headers=WRITE
    )


def sign_in(client, username="student_a"):
    assert register(client, username).status_code == 201
    assert login(client, username).status_code == 200


def test_search_booking_and_cancel_release_only_selected_interval(client, resources):
    seats = resources["seats"]
    rooms = client.get("/api/v1/rooms", params={"campus": "Demo", "floor": 2}).json()
    assert rooms["items"][0]["capacity"] == 2
    assert client.get("/api/v1/rooms", params={"campus": "absent"}).json()["total"] == 0
    sign_in(client)
    first = book(client, seats[0])
    assert first.status_code == 201
    second = book(client, seats[0], **interval("10:00", "11:00"))
    assert second.status_code == 201  # Adjacent, same student, no global count cap.
    listing = client.get(f"/api/v1/rooms/{resources['room']}/seats", params=interval()).json()
    assert {x["id"]: x["available"] for x in listing["items"]} == {seats[0]: False, seats[1]: True}
    mine = client.get("/api/v1/bookings").json()
    assert mine["total"] == 2
    cancelled = client.post(f"/api/v1/bookings/{first.json()['id']}/cancel", json={}, headers=WRITE)
    assert cancelled.status_code == 200 and cancelled.json()["status"] == "CANCELLED"
    assert (
        client.post(
            f"/api/v1/bookings/{first.json()['id']}/cancel", json={}, headers=WRITE
        ).status_code
        == 200
    )
    listing = client.get(f"/api/v1/rooms/{resources['room']}/seats", params=interval()).json()
    assert listing["items"][0]["available"] is True
    assert client.get("/api/v1/bookings").json()["total"] == 2


def test_same_student_different_seat_overlap_is_rejected_but_future_non_overlap_allowed(
    client, resources
):
    sign_in(client)
    assert book(client, resources["seats"][0]).status_code == 201
    overlap = book(client, resources["seats"][1], **interval("09:30", "10:30"))
    assert overlap.status_code == 409
    assert overlap.json()["error"]["code"] == "USER_CONFLICT"
    assert book(client, resources["seats"][1], **interval(days=2)).status_code == 201


@pytest.mark.parametrize(
    "times",
    [
        interval("07:30", "08:30"),
        interval("21:30", "22:30"),
        interval("09:15", "10:00"),
        interval("10:00", "09:00"),
        interval(days=-1),
        interval(days=7),
        {"starts_at": "2030-01-01T09:00:00", "ends_at": "2030-01-01T10:00:00"},
    ],
)
def test_server_rejects_invalid_boundaries_and_window(client, resources, times):
    sign_in(client)
    assert book(client, resources["seats"][0], **times).status_code == 422


def test_offsets_describe_same_real_time_and_empty_query_is_not_false_availability(
    client, resources
):
    sign_in(client)
    local = interval()
    starts = datetime.fromisoformat(local["starts_at"])
    ends = datetime.fromisoformat(local["ends_at"])
    utc = {
        "starts_at": starts.astimezone(ZoneInfo("UTC")).isoformat(),
        "ends_at": ends.astimezone(ZoneInfo("UTC")).isoformat(),
    }
    assert book(client, resources["seats"][0], **utc).status_code == 201
    assert book(client, resources["seats"][0], **local).status_code == 409
    assert client.get(f"/api/v1/rooms/{resources['room']}/seats").status_code == 422


def test_private_history_ownership_and_unauthenticated_booking(client, resources):
    assert book(client, resources["seats"][0]).status_code == 401
    sign_in(client)
    booking = book(client, resources["seats"][0]).json()
    assert client.post("/api/v1/auth/logout", headers=WRITE).status_code == 204
    sign_in(client, "student_b")
    assert client.get("/api/v1/bookings").json()["total"] == 0
    assert (
        client.post(f"/api/v1/bookings/{booking['id']}/cancel", json={}, headers=WRITE).status_code
        == 404
    )
    assert client.get("/api/v1/bookings", params={"page_size": 101}).status_code == 422


@pytest.mark.parametrize(
    "same_user,same_seat,adjacent", [(False, True, False), (True, False, False), (True, True, True)]
)
def test_concurrent_requests_are_atomic(
    application, client, resources, same_user, same_seat, adjacent
):
    a, b = TestClient(application), TestClient(application)
    try:
        sign_in(a, "racer_a")
        if same_user:
            b.cookies.update(a.cookies)
        else:
            sign_in(b, "racer_b")
        gate = Barrier(2)

        def submit(which):
            gate.wait(timeout=5)
            return book(
                a if which == 0 else b,
                resources["seats"][0 if same_seat or which == 0 else 1],
                **(interval("10:00", "11:00") if adjacent and which else interval()),
            ).status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = sorted(pool.map(submit, [0, 1]))
        assert results == ([201, 201] if adjacent else [201, 409])
    finally:
        a.close()
        b.close()
