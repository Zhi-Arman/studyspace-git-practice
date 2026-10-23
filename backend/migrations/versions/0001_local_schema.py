"""Initial local reservation schema. Migration fields remain frozen."""

import sqlalchemy as sa
from alembic import op

revision = "0001_local"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(32), nullable=False, unique=True),
        sa.Column("display_name", sa.String(60), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("role", sa.String(12), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("disabled_at", sa.DateTime),
        sa.Column("anonymized_at", sa.DateTime),
    )
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_expires_at", "sessions", ["expires_at"])
    op.create_table(
        "login_attempts",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("failures", sa.Integer, nullable=False),
        sa.Column("window_start", sa.DateTime, nullable=False),
    )
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("campus", sa.String(60), nullable=False),
        sa.Column("building", sa.String(60), nullable=False),
        sa.Column("floor", sa.Integer, nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("description", sa.String(240), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("opens_at", sa.Integer, nullable=False),
        sa.Column("closes_at", sa.Integer, nullable=False),
    )
    op.create_table(
        "seats",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("code", sa.String(24), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.UniqueConstraint("room_id", "code", name="uq_room_seat"),
    )
    op.create_index("ix_seats_room_id", "seats", ["room_id"])
    op.create_table(
        "opening_exceptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("day", sa.Date, nullable=False),
        sa.Column("closed", sa.Boolean, nullable=False),
        sa.Column("opens_at", sa.Integer, nullable=False),
        sa.Column("closes_at", sa.Integer, nullable=False),
        sa.UniqueConstraint("room_id", "day", name="uq_room_day"),
    )
    op.create_index("ix_opening_exceptions_room_id", "opening_exceptions", ["room_id"])
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("seat_id", sa.Integer, sa.ForeignKey("seats.id"), nullable=False),
        sa.Column("business_date", sa.Date, nullable=False),
        sa.Column("starts_at", sa.DateTime, nullable=False),
        sa.Column("ends_at", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("cancelled_at", sa.DateTime),
        sa.Column("cancelled_by", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("cancellation_reason", sa.String(240)),
    )
    op.create_index("ix_bookings_business_date", "bookings", ["business_date"])
    op.create_index("ix_booking_seat_time", "bookings", ["seat_id", "starts_at", "ends_at"])
    op.create_index("ix_booking_user_time", "bookings", ["user_id", "starts_at", "ends_at"])
    op.create_table(
        "policy",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("advance_days", sa.Integer, nullable=False),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("target_type", sa.String(20), nullable=False),
        sa.Column("target_id", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])
    op.execute("INSERT INTO policy (id, advance_days) VALUES (1, 7)")


def downgrade():
    for table in [
        "audit_events",
        "policy",
        "bookings",
        "opening_exceptions",
        "seats",
        "rooms",
        "login_attempts",
        "sessions",
        "users",
    ]:
        op.drop_table(table)
