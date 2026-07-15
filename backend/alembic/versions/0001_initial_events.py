"""Initial events schema

Revision ID: 0001_initial_events
Revises:
Create Date: 2026-07-15 00:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001_initial_events"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("event_id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), nullable=True),
        sa.Column("worker_id", sa.String(length=64), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_events_timestamp"), "events", ["timestamp"], unique=False)
    op.create_index(op.f("ix_events_source"), "events", ["source"], unique=False)
    op.create_index(op.f("ix_events_event_type"), "events", ["event_type"], unique=False)
    op.create_index(op.f("ix_events_plant_id"), "events", ["plant_id"], unique=False)
    op.create_index(op.f("ix_events_zone_id"), "events", ["zone_id"], unique=False)
    op.create_index(op.f("ix_events_equipment_id"), "events", ["equipment_id"], unique=False)
    op.create_index(op.f("ix_events_worker_id"), "events", ["worker_id"], unique=False)
    op.create_index(op.f("ix_events_severity"), "events", ["severity"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_events_severity"), table_name="events")
    op.drop_index(op.f("ix_events_worker_id"), table_name="events")
    op.drop_index(op.f("ix_events_equipment_id"), table_name="events")
    op.drop_index(op.f("ix_events_zone_id"), table_name="events")
    op.drop_index(op.f("ix_events_plant_id"), table_name="events")
    op.drop_index(op.f("ix_events_event_type"), table_name="events")
    op.drop_index(op.f("ix_events_source"), table_name="events")
    op.drop_index(op.f("ix_events_timestamp"), table_name="events")
    op.drop_table("events")
