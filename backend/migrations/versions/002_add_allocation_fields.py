"""Add allocation fields to proof_jobs

Revision ID: 002
Revises: 001
Create Date: 2025-12-08 17:46:33

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('proof_jobs', sa.Column('jediswap_pct', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('proof_jobs', sa.Column('ekubo_pct', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('proof_jobs', sa.Column('jediswap_risk', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('proof_jobs', sa.Column('ekubo_risk', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    op.drop_column('proof_jobs', 'ekubo_risk')
    op.drop_column('proof_jobs', 'jediswap_risk')
    op.drop_column('proof_jobs', 'ekubo_pct')
    op.drop_column('proof_jobs', 'jediswap_pct')
