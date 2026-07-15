"""Phase 2 digital twin, context, and actions

Revision ID: 0002_phase2_digital_twin_context_actions
Revises: 0001_initial_events
Create Date: 2026-07-15 00:00:00.000001

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0002_phase2_digital_twin_context_actions"
down_revision = "0001_initial_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plant_states",
        sa.Column("plant_id", sa.String(length=64), primary_key=True),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "zone_states",
        sa.Column("zone_id", sa.String(length=64), primary_key=True),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_zone_states_plant_id", "zone_states", ["plant_id"], unique=False)

    op.create_table(
        "equipment_states",
        sa.Column("equipment_id", sa.String(length=64), primary_key=True),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_equipment_states_plant_id", "equipment_states", ["plant_id"], unique=False)
    op.create_index("ix_equipment_states_zone_id", "equipment_states", ["zone_id"], unique=False)

    op.create_table(
        "worker_states",
        sa.Column("worker_id", sa.String(length=64), primary_key=True),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=True),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_worker_states_plant_id", "worker_states", ["plant_id"], unique=False)
    op.create_index("ix_worker_states_zone_id", "worker_states", ["zone_id"], unique=False)

    op.create_table(
        "permit_states",
        sa.Column("permit_id", sa.String(length=64), primary_key=True),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_permit_states_plant_id", "permit_states", ["plant_id"], unique=False)
    op.create_index("ix_permit_states_zone_id", "permit_states", ["zone_id"], unique=False)

    op.create_table(
        "maintenance_states",
        sa.Column("maintenance_id", sa.String(length=64), primary_key=True),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), nullable=True),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_maintenance_states_plant_id", "maintenance_states", ["plant_id"], unique=False)
    op.create_index("ix_maintenance_states_zone_id", "maintenance_states", ["zone_id"], unique=False)
    op.create_index("ix_maintenance_states_equipment_id", "maintenance_states", ["equipment_id"], unique=False)

    op.create_table(
        "sensor_states",
        sa.Column("sensor_id", sa.String(length=64), primary_key=True),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), nullable=True),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_sensor_states_plant_id", "sensor_states", ["plant_id"], unique=False)
    op.create_index("ix_sensor_states_zone_id", "sensor_states", ["zone_id"], unique=False)
    op.create_index("ix_sensor_states_equipment_id", "sensor_states", ["equipment_id"], unique=False)

    op.create_table(
        "hazard_states",
        sa.Column("hazard_id", sa.String(length=64), primary_key=True),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("equipment_id", sa.String(length=64), nullable=True),
        sa.Column("source_event_id", sa.String(length=36), nullable=True),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_hazard_states_plant_id", "hazard_states", ["plant_id"], unique=False)
    op.create_index("ix_hazard_states_zone_id", "hazard_states", ["zone_id"], unique=False)
    op.create_index("ix_hazard_states_equipment_id", "hazard_states", ["equipment_id"], unique=False)

    op.create_table(
        "twin_state_snapshots",
        sa.Column("context_id", sa.String(length=36), primary_key=True),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("serialized_state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_twin_state_snapshots_event_id", "twin_state_snapshots", ["event_id"], unique=False)
    op.create_index("ix_twin_state_snapshots_plant_id", "twin_state_snapshots", ["plant_id"], unique=False)
    op.create_index("ix_twin_state_snapshots_timestamp", "twin_state_snapshots", ["timestamp"], unique=False)

    op.create_table(
        "context_snapshots",
        sa.Column("context_id", sa.String(length=36), primary_key=True),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("serialized_context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_context_snapshots_event_id", "context_snapshots", ["event_id"], unique=False)
    op.create_index("ix_context_snapshots_plant_id", "context_snapshots", ["plant_id"], unique=False)
    op.create_index("ix_context_snapshots_zone_id", "context_snapshots", ["zone_id"], unique=False)
    op.create_index("ix_context_snapshots_timestamp", "context_snapshots", ["timestamp"], unique=False)

    op.create_table(
        "action_events",
        sa.Column("action_id", sa.String(length=36), primary_key=True),
        sa.Column("action_type", sa.String(length=128), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("reason", sa.String(length=512), nullable=False),
        sa.Column("generated_by", sa.String(length=128), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("context_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("action_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("plant_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_action_events_action_type", "action_events", ["action_type"], unique=False)
    op.create_index("ix_action_events_context_id", "action_events", ["context_id"], unique=False)
    op.create_index("ix_action_events_plant_id", "action_events", ["plant_id"], unique=False)
    op.create_index("ix_action_events_timestamp", "action_events", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_action_events_timestamp", table_name="action_events")
    op.drop_index("ix_action_events_plant_id", table_name="action_events")
    op.drop_index("ix_action_events_context_id", table_name="action_events")
    op.drop_index("ix_action_events_action_type", table_name="action_events")
    op.drop_table("action_events")

    op.drop_index("ix_context_snapshots_timestamp", table_name="context_snapshots")
    op.drop_index("ix_context_snapshots_zone_id", table_name="context_snapshots")
    op.drop_index("ix_context_snapshots_plant_id", table_name="context_snapshots")
    op.drop_index("ix_context_snapshots_event_id", table_name="context_snapshots")
    op.drop_table("context_snapshots")

    op.drop_index("ix_twin_state_snapshots_timestamp", table_name="twin_state_snapshots")
    op.drop_index("ix_twin_state_snapshots_plant_id", table_name="twin_state_snapshots")
    op.drop_index("ix_twin_state_snapshots_event_id", table_name="twin_state_snapshots")
    op.drop_table("twin_state_snapshots")

    op.drop_index("ix_hazard_states_equipment_id", table_name="hazard_states")
    op.drop_index("ix_hazard_states_zone_id", table_name="hazard_states")
    op.drop_index("ix_hazard_states_plant_id", table_name="hazard_states")
    op.drop_table("hazard_states")

    op.drop_index("ix_sensor_states_equipment_id", table_name="sensor_states")
    op.drop_index("ix_sensor_states_zone_id", table_name="sensor_states")
    op.drop_index("ix_sensor_states_plant_id", table_name="sensor_states")
    op.drop_table("sensor_states")

    op.drop_index("ix_maintenance_states_equipment_id", table_name="maintenance_states")
    op.drop_index("ix_maintenance_states_zone_id", table_name="maintenance_states")
    op.drop_index("ix_maintenance_states_plant_id", table_name="maintenance_states")
    op.drop_table("maintenance_states")

    op.drop_index("ix_permit_states_zone_id", table_name="permit_states")
    op.drop_index("ix_permit_states_plant_id", table_name="permit_states")
    op.drop_table("permit_states")

    op.drop_index("ix_worker_states_zone_id", table_name="worker_states")
    op.drop_index("ix_worker_states_plant_id", table_name="worker_states")
    op.drop_table("worker_states")

    op.drop_index("ix_equipment_states_zone_id", table_name="equipment_states")
    op.drop_index("ix_equipment_states_plant_id", table_name="equipment_states")
    op.drop_table("equipment_states")

    op.drop_index("ix_zone_states_plant_id", table_name="zone_states")
    op.drop_table("zone_states")

    op.drop_table("plant_states")
