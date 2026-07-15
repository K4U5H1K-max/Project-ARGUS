"""Phase 3 reliability persistence and traceability.

Revision ID: 0003_phase3_reliability
Revises: 0002_phase2_digital_twin_context_actions
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_phase3_reliability"
down_revision = "0002_phase2_digital_twin_context_actions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Phase 1 predates external identifiers and trace/version metadata.
    op.add_column("events", sa.Column("external_event_id", sa.String(128), nullable=True))
    op.add_column("events", sa.Column("event_hash", sa.String(64), nullable=True))
    op.add_column("events", sa.Column("processing_version", sa.Integer(), nullable=False, server_default="1"))
    op.create_index("ix_events_external_event_id", "events", ["external_event_id"])
    op.create_index("ix_events_event_hash", "events", ["event_hash"])
    op.create_unique_constraint("uq_events_source_external_event_id", "events", ["source", "external_event_id"])
    # Phase 2 stored UUID references as text before relationships were enforced.
    for table in ("twin_state_snapshots", "context_snapshots"):
        op.alter_column(table, "event_id", type_=postgresql.UUID(as_uuid=True), postgresql_using="event_id::uuid")
    op.create_table("processed_events",
        sa.Column("processed_event_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_event_id", sa.String(128), nullable=False), sa.Column("source", sa.String(128), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("checksum", sa.String(64), nullable=False), sa.Column("processing_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False),
        sa.Column("trace", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("external_event_id", "source", name="uq_processed_events_external_source"))
    for column in ("external_event_id", "source", "checksum", "event_id"): op.create_index(f"ix_processed_events_{column}", "processed_events", [column])
    op.create_table("outbox_messages",
        sa.Column("outbox_id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("topic", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(128), nullable=False), sa.Column("aggregate_type", sa.String(128), nullable=False), sa.Column("aggregate_id", sa.String(128), nullable=False), sa.Column("partition_key", sa.String(128), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False), sa.Column("headers", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"), sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"), sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True)), sa.Column("delivered_at", sa.DateTime(timezone=True)), sa.Column("dead_lettered_at", sa.DateTime(timezone=True)), sa.Column("last_error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
    for column in ("topic", "event_type", "status", "next_attempt_at", "checksum"): op.create_index(f"ix_outbox_messages_{column}", "outbox_messages", [column])
    op.create_index("ix_outbox_messages_due", "outbox_messages", ["status", "next_attempt_at"])
    op.create_table("audit_logs",
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("actor", sa.String(128), nullable=False), sa.Column("action", sa.String(128), nullable=False), sa.Column("reason", sa.String(256), nullable=False),
        sa.Column("old_value", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("new_value", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("processor", sa.String(128)), sa.Column("rule", sa.String(128)), sa.Column("version", sa.Integer(), nullable=False, server_default="1"), sa.Column("context", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    for column in ("actor", "action", "processor", "rule"): op.create_index(f"ix_audit_logs_{column}", "audit_logs", [column])
    op.add_column("twin_state_snapshots", sa.Column("processor_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("twin_state_snapshots", sa.Column("trace_metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.add_column("context_snapshots", sa.Column("processor_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("context_snapshots", sa.Column("trace_metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.add_column("action_events", sa.Column("rule_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("action_events", sa.Column("trace_metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.create_foreign_key("fk_twin_snapshots_event", "twin_state_snapshots", "events", ["event_id"], ["event_id"], ondelete="CASCADE")
    op.create_foreign_key("fk_context_snapshots_event", "context_snapshots", "events", ["event_id"], ["event_id"], ondelete="CASCADE")
    op.create_foreign_key("fk_actions_context", "action_events", "context_snapshots", ["context_id"], ["context_id"], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_table("audit_logs"); op.drop_table("outbox_messages"); op.drop_table("processed_events")
    op.drop_constraint("fk_actions_context", "action_events", type_="foreignkey")
    op.drop_constraint("fk_context_snapshots_event", "context_snapshots", type_="foreignkey")
    op.drop_constraint("fk_twin_snapshots_event", "twin_state_snapshots", type_="foreignkey")
    for table, columns in (("twin_state_snapshots", ("processor_version", "trace_metadata")), ("context_snapshots", ("processor_version", "trace_metadata")), ("action_events", ("rule_version", "trace_metadata"))):
        for column in columns: op.drop_column(table, column)
    op.drop_constraint("uq_events_source_external_event_id", "events", type_="unique")
    op.drop_index("ix_events_event_hash", table_name="events")
    op.drop_index("ix_events_external_event_id", table_name="events")
    op.drop_column("events", "processing_version"); op.drop_column("events", "event_hash"); op.drop_column("events", "external_event_id")
