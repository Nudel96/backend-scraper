from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("symbol", sa.String(20), nullable=False, unique=True),
        sa.Column("kind", sa.String(20), nullable=False),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("trace_id", sa.String(36), nullable=False, unique=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
    )
    op.create_index(
        "ix_events_asset_kind_ts", "events", ["asset_id", "kind", "ingested_at"], unique=False
    )
    op.create_table(
        "indicators",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("key", sa.String(50), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.UniqueConstraint("asset_id", "key", "ts"),
    )
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total", sa.Integer, nullable=False),
        sa.Column("breakdown", sa.JSON, nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
    )
    op.create_index("ix_scores_asset_ts", "scores", ["asset_id", "ts"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scores_asset_ts", table_name="scores")
    op.drop_table("scores")
    op.drop_table("indicators")
    op.drop_index("ix_events_asset_kind_ts", table_name="events")
    op.drop_table("events")
    op.drop_table("assets")
