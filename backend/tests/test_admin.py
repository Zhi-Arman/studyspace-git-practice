"""Administrative side effects, authorization and snapshot statistics."""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import text
from tests.test_bookings import book, interval, sign_in
from tests.test_bookings import resources as resources
from tests.test_local_accounts import WRITE, login, register


def make_admin(client, engine, username="admin_a"):
    assert register(client, username).status_code == 201
    with engine.begin() as db:
        db.execute(text("UPDATE users SET role='ADMIN' WHERE username=:name"), {"name": username})
    assert login(client, username).status_code == 200
    return client.get("/api/v1/auth/me").json()


def room_payload(**changes):
    return {
        "name": "演示自习室",
        "campus": "Demo",
        "building": "Library",
        "floor": 2,
        "kind": "STUDY_ROOM",
        "enabled": True,
        "opens_at": "08:00",
        "closes_at": "22:00",
        "reason": "Local course test",
        **changes,
    }


def test_admin_endpoints_deny_students_and_public_registration_cannot_grant_role(client, resources):
    assert client.get("/api/v1/admin/rooms").status_code == 401
    sign_in(client)
    for path in ["rooms", "users", "bookings", "statistics"]:
        assert client.get("/api/v1/admin/" + path).status_code == 403


def test_room_seat_management_uniqueness_and_disabled_room_visibility(client, engine, resources):
    make_admin(client, engine)
    added = client.post("/api/v1/admin/rooms", json=room_payload(name="演示教室B"), headers=WRITE)
    assert added.status_code == 201
    room_id = added.json()["id"]
    assert (
        client.post(
            "/api/v1/admin/seats", json={"room_id": room_id, "code": "B01"}, headers=WRITE
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/admin/seats", json={"room_id": room_id, "code": "B01"}, headers=WRITE
        ).status_code
        == 409
    )
    assert client.get(f"/api/v1/admin/rooms/{room_id}/seats").json()["items"][0]["code"] == "B01"
    assert (
        client.put(
            f"/api/v1/admin/rooms/{room_id}", json=room_payload(enabled=False), headers=WRITE
        ).status_code
        == 200
    )
    assert all(x["id"] != room_id for x in client.get("/api/v1/rooms").json()["items"])
    assert any(
        x["id"] == room_id and not x["enabled"]
        for x in client.get("/api/v1/admin/rooms").json()["items"]
    )


@pytest.mark.parametrize("action", ["disable_room", "disable_seat", "shrink_hours", "close_day"])
def test_resource_changes_atomically_cancel_affected_bookings(client, engine, resources, action):
    sign_in(client)
    assert book(client, resources["seats"][0]).status_code == 201
    make_admin(client, engine)
    if action == "disable_room":
        result = client.put(
            f"/api/v1/admin/rooms/{resources['room']}",
            json=room_payload(enabled=False),
            headers=WRITE,
        )
    elif action == "disable_seat":
        result = client.put(
            f"/api/v1/admin/seats/{resources['seats'][0]}",
            json={
                "room_id": resources["room"],
                "code": "A01",
                "enabled": False,
                "reason": "Maintenance",
            },
            headers=WRITE,
        )
    elif action == "shrink_hours":
        result = client.put(
            f"/api/v1/admin/rooms/{resources['room']}",
            json=room_payload(opens_at="10:00"),
            headers=WRITE,
        )
    else:
        result = client.post(
            "/api/v1/admin/opening-exceptions",
            json={
                "room_id": resources["room"],
                "day": interval()["starts_at"][:10],
                "closed": True,
                "reason": "Closed for local demonstration",
            },
            headers=WRITE,
        )
    assert result.status_code in {200, 201}
    records = client.get("/api/v1/admin/bookings").json()["items"]
    assert records[0]["status"] == "CANCELLED"
    assert records[0]["cancellation_reason"]
    # Re-enabling must never resurrect a cancelled reservation.
    if action == "disable_room":
        client.put(f"/api/v1/admin/rooms/{resources['room']}", json=room_payload(), headers=WRITE)
        assert client.get("/api/v1/admin/bookings").json()["items"][0]["status"] == "CANCELLED"


def test_user_disable_revokes_sessions_cancels_records_and_last_admin_is_protected(
    client, engine, resources
):
    sign_in(client)
    student = client.get("/api/v1/auth/me").json()
    token = client.cookies["studyspace_session"]
    assert book(client, resources["seats"][0]).status_code == 201
    admin = make_admin(client, engine)
    denied = client.put(
        f"/api/v1/admin/users/{admin['id']}",
        json={"role": "STUDENT", "enabled": True, "reason": "Test"},
        headers=WRITE,
    )
    assert denied.status_code == 409
    result = client.put(
        f"/api/v1/admin/users/{student['id']}",
        json={"role": "STUDENT", "enabled": False, "reason": "Test disable"},
        headers=WRITE,
    )
    assert result.status_code == 200
    assert client.get("/api/v1/admin/bookings").json()["items"][0]["status"] == "CANCELLED"
    client.cookies.set("studyspace_session", token, domain="testserver.local", path="/")
    assert client.get("/api/v1/auth/me").status_code == 401


def test_admin_cancellation_requires_reason_and_statistics_use_consistent_as_of(
    client, engine, resources
):
    sign_in(client)
    first = book(client, resources["seats"][0]).json()
    assert book(client, resources["seats"][1], **interval("11:00", "12:00")).status_code == 201
    make_admin(client, engine)
    assert (
        client.post(f"/api/v1/bookings/{first['id']}/cancel", json={}, headers=WRITE).status_code
        == 422
    )
    assert (
        client.post(
            f"/api/v1/bookings/{first['id']}/cancel",
            json={"reason": "Room maintenance"},
            headers=WRITE,
        ).status_code
        == 200
    )
    day = interval()["starts_at"][:10]
    stats = client.get("/api/v1/admin/statistics", params={"day": day}).json()
    assert (stats["created"], stats["cancelled"], stats["active"]) == (2, 1, 1)
    assert stats["as_of"].endswith("Z")
    assert client.get("/api/v1/admin/bookings", params={"username": "absent"}).json()["total"] == 0
    expired = (date.today() - timedelta(days=200)).isoformat()
    assert client.get("/api/v1/admin/statistics", params={"day": expired}).status_code == 410


def test_policy_can_only_narrow_window_and_closed_dates_show_no_available_seats(
    client, engine, resources
):
    make_admin(client, engine)
    assert (
        client.put(
            "/api/v1/admin/policy", json={"advance_days": 8, "reason": "Too wide"}, headers=WRITE
        ).status_code
        == 422
    )
    assert (
        client.put(
            "/api/v1/admin/policy",
            json={"advance_days": 3, "reason": "Course schedule"},
            headers=WRITE,
        ).status_code
        == 200
    )
    assert client.get("/api/v1/policy").json()["advance_days"] == 3
    day = interval()["starts_at"][:10]
    closed = client.post(
        "/api/v1/admin/opening-exceptions",
        json={"room_id": resources["room"], "day": day, "closed": True, "reason": "Closed"},
        headers=WRITE,
    )
    assert closed.status_code == 201
    result = client.get(f"/api/v1/rooms/{resources['room']}/seats", params=interval()).json()
    assert result["room"]["closed"] is True
    assert not any(x["available"] for x in result["items"])
    assert (
        client.post(
            f"/api/v1/admin/opening-exceptions/{closed.json()['id']}/remove",
            json={"reason": "Reopen"},
            headers=WRITE,
        ).status_code
        == 200
    )
    assert (
        client.get(f"/api/v1/rooms/{resources['room']}/seats", params=interval()).json()["items"][
            0
        ]["available"]
        is True
    )


def test_exact_24h_midnight_interval_allowed_only_when_room_open_all_day(
    client, engine, resources, monkeypatch
):
    sign_in(client)
    with engine.begin() as db:
        db.execute(text("UPDATE rooms SET opens_at=0, closes_at=1440"))
    monkeypatch.setattr("app.reservations_api.utcnow", lambda: datetime(2030, 1, 1, 0, 0))
    result = book(
        client,
        resources["seats"][0],
        starts_at="2030-01-02T00:00:00+08:00",
        ends_at="2030-01-03T00:00:00+08:00",
    )
    assert result.status_code == 201
    assert result.json()["business_date"] == "2030-01-02"


def test_admin_cannot_retroactively_cancel_completed_bookings(client, engine, resources):
    sign_in(client)
    booking = book(client, resources["seats"][0]).json()
    with engine.begin() as db:
        db.execute(
            text(
                "UPDATE bookings SET starts_at='2000-01-01 01:00:00', "
                "ends_at='2000-01-01 02:00:00' WHERE id=:id"
            ),
            {"id": booking["id"]},
        )
    make_admin(client, engine)
    result = client.post(
        f"/api/v1/bookings/{booking['id']}/cancel", json={"reason": "Too late"}, headers=WRITE
    )
    assert result.status_code == 409


def test_touching_disabled_account_does_not_restart_retention_clock(client, engine):
    register(client, "disabled_user")
    with engine.begin() as db:
        db.execute(
            text(
                "UPDATE users SET enabled=0, disabled_at='2000-01-01 00:00:00' "
                "WHERE username='disabled_user'"
            )
        )
        user_id = db.execute(
            text("SELECT id FROM users WHERE username='disabled_user'")
        ).scalar_one()
    make_admin(client, engine)
    assert (
        client.put(
            f"/api/v1/admin/users/{user_id}",
            json={"role": "STUDENT", "enabled": False, "reason": "Retain disabled"},
            headers=WRITE,
        ).status_code
        == 200
    )
    with engine.connect() as db:
        assert str(
            db.execute(
                text("SELECT disabled_at FROM users WHERE id=:id"), {"id": user_id}
            ).scalar_one()
        ).startswith("2000-01-01")
