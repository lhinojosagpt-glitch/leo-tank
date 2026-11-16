"""Persist deterministic design-assistant studies and candidate runs."""

from alembic import op
import sqlalchemy as sa

revision = "0002_design_assistant"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "design_studies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_run_id", sa.String(36), sa.ForeignKey("calculation_runs.id"), nullable=False),
        sa.Column("baseline_revision_id", sa.String(36), sa.ForeignKey("scenario_revisions.id"), nullable=False),
        sa.Column("target_check_id", sa.String(120), nullable=False),
        sa.Column("objective", sa.String(60), nullable=False),
        sa.Column("target_utilization", sa.Float(), nullable=False),
        sa.Column("variables_json", sa.JSON(), nullable=False),
        sa.Column("search_space_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("engine_version", sa.String(40), nullable=False),
        sa.Column("standard_profile", sa.String(80), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_design_studies_source_run_id", "design_studies", ["source_run_id"])
    op.create_index("ix_design_studies_baseline_revision_id", "design_studies", ["baseline_revision_id"])
    op.create_index("ix_design_studies_target_check_id", "design_studies", ["target_check_id"])
    op.create_table(
        "design_study_variants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("study_id", sa.String(36), sa.ForeignKey("design_studies.id"), nullable=False),
        sa.Column("candidate_run_id", sa.String(36), sa.ForeignKey("calculation_runs.id"), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("changes_json", sa.JSON(), nullable=False),
        sa.Column("values_tested_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("passing", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_design_study_variants_study_id", "design_study_variants", ["study_id"])
    op.create_index("ix_design_study_variants_candidate_run_id", "design_study_variants", ["candidate_run_id"])


def downgrade() -> None:
    op.drop_table("design_study_variants")
    op.drop_table("design_studies")
