"""Add decision_id to proof_jobs

Revision ID: 005
Revises: 004
Create Date: 2026-01-25 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('proof_jobs', sa.Column('decision_id', sa.Integer(), nullable=True))
    op.create_index('ix_proof_jobs_decision_id', 'proof_jobs', ['decision_id'])


def downgrade() -> None:
    op.drop_index('ix_proof_jobs_decision_id', table_name='proof_jobs')
    op.drop_column('proof_jobs', 'decision_id')
