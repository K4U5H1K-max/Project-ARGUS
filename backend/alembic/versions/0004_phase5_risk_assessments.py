"""Phase 5 compound risk assessment persistence."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0004_phase5_risk_assessments"; down_revision="0003_phase3_reliability"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("risk_assessments",sa.Column("risk_id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("plant_id",sa.String(64),nullable=False),sa.Column("zone_id",sa.String(64),nullable=False),sa.Column("timestamp",sa.DateTime(timezone=True),nullable=False),sa.Column("revision",sa.Integer(),nullable=False,server_default="1"),sa.Column("risk_score",sa.Float(),nullable=False),sa.Column("risk_level",sa.String(16),nullable=False),sa.Column("confidence",sa.Float(),nullable=False),sa.Column("status",sa.String(16),nullable=False,server_default="ACTIVE"),sa.Column("explanation",postgresql.JSONB(),nullable=False),sa.Column("recommendation",postgresql.JSONB(),nullable=False),sa.Column("processor_version",sa.Integer(),nullable=False,server_default="1"),sa.Column("context_id",sa.String(36),sa.ForeignKey("context_snapshots.context_id"),nullable=False),sa.Column("event_id",sa.String(36),nullable=False),sa.Column("graph_revision",sa.Integer(),nullable=False),sa.Column("twin_revision",sa.Integer(),nullable=False),sa.Column("trace",postgresql.JSONB(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),nullable=False))
    for c in ("plant_id","zone_id","timestamp","risk_level","status","context_id","event_id"): op.create_index(f"ix_risk_assessments_{c}","risk_assessments",[c])
def downgrade(): op.drop_table("risk_assessments")
