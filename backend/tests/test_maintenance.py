"""CLI maintenance works on actual SQLite files, without real personal data."""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

from sqlalchemy import inspect, text

from app.migration import migrate
from app.security import utcnow
from tests.test_bookings import resources as resources
from tests.test_local_accounts import login, register


def cli(database, *args):
    environment = {**os.environ, "APP_ENV": "test", "DATABASE_URL": f"sqlite:///{database}"}
    return subprocess.run(
        [sys.executable, "-m", "app.cli", *map(str, args)],
        cwd=Path(__file__).parents[1],
        env=environment,
        text=True,
        capture_output=True,
        timeout=20,
    )


def test_fresh_cli_seed_is_idempotent_and_no_default_admin_is_created(tmp_path):
    database = tmp_path / "fresh.sqlite"
    first = cli(database, "init-local")
    assert first.returncode == 0, first.stderr
    assert cli(database, "init-local").returncode == 0
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT count(*) FROM rooms").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM seats").fetchone()[0] == 12
        assert db.execute("SELECT count(*) FROM users").fetchone()[0] == 0
    private = tmp_path / "password.txt"
    private.write_text("Local-test-password42!")
    private.chmod(0o600)
    created = cli(
        database,
        "create-admin",
        "--username",
        "localadmin",
        "--name",
        "演示管理员",
        "--password-file",
        private,
    )
    assert created.returncode == 0, created.stderr
    assert "Local-test-password42!" not in created.stdout + created.stderr
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT role FROM users").fetchone()[0] == "ADMIN"


def test_backup_restore_snapshot_uses_new_file_and_revokes_old_sessions(
    client, database_path, tmp_path
):
    assert register(client).status_code == 201
    assert login(client).status_code == 200
    backup = tmp_path / "snapshot.sqlite"
    saved = cli(database_path, "backup", "--output", backup)
    assert saved.returncode == 0, saved.stderr
    assert register(client, "after_backup").status_code == 201
    restored = tmp_path / "restored.sqlite"
    result = cli(database_path, "restore", "--backup", backup, "--output", restored)
    assert result.returncode == 0, result.stderr
    with sqlite3.connect(restored) as db:
        assert db.execute("SELECT count(*) FROM users").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM sessions").fetchone()[0] == 0
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert (
        cli(database_path, "restore", "--backup", backup, "--output", database_path).returncode != 0
    )
    with sqlite3.connect(database_path) as db:
        assert db.execute("SELECT count(*) FROM users").fetchone()[0] == 2


def test_retention_deletes_only_expired_data_and_anonymizes_eligible_users(
    client, engine, database_path, resources
):
    assert register(client, "expired_user").status_code == 201
    assert register(client, "recent_user").status_code == 201
    now = utcnow()
    with engine.begin() as db:
        db.execute(
            text("UPDATE users SET enabled=0, disabled_at=:old WHERE username='expired_user'"),
            {"old": (now - timedelta(days=40)).isoformat(sep=" ")},
        )
        db.execute(
            text("UPDATE users SET enabled=0, disabled_at=:recent WHERE username='recent_user'"),
            {"recent": (now - timedelta(days=20)).isoformat(sep=" ")},
        )
        user_id = db.execute(
            text("SELECT id FROM users WHERE username='expired_user'")
        ).scalar_one()
        db.execute(
            text("UPDATE audit_events SET created_at=:old WHERE actor_id=:user"),
            {"old": (now - timedelta(days=202)).isoformat(sep=" "), "user": user_id},
        )
        db.execute(
            text(
                "INSERT INTO bookings(user_id,seat_id,business_date,starts_at,ends_at,created_at) "
                "VALUES(:user,:seat,:day,:start,:end,:created)"
            ),
            {
                "user": user_id,
                "seat": resources["seats"][0],
                "day": (now - timedelta(days=201)).date().isoformat(),
                "start": (now - timedelta(days=201)).isoformat(sep=" "),
                "end": (now - timedelta(days=200)).isoformat(sep=" "),
                "created": (now - timedelta(days=202)).isoformat(sep=" "),
            },
        )
    result = cli(database_path, "cleanup")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["anonymized_users"] == 1
    with engine.connect() as db:
        assert db.execute(text("SELECT count(*) FROM bookings")).scalar_one() == 0
        assert (
            db.execute(text("SELECT username FROM users WHERE id=:id"), {"id": user_id})
            .scalar_one()
            .startswith("deleted_")
        )
        assert (
            db.execute(text("SELECT username FROM users WHERE username='recent_user'")).scalar_one()
            == "recent_user"
        )


def test_migration_roundtrip_preserves_a_reproducible_schema(engine, client):
    migrate(engine, "base")
    assert "users" not in inspect(engine).get_table_names()
    migrate(engine)
    assert {"users", "sessions", "rooms", "seats", "bookings"}.issubset(
        inspect(engine).get_table_names()
    )
