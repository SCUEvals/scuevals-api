"""Add evaluation data

Revision ID: 889c8e4f8974
Revises: 20f4c8ae647c
Create Date: 2017-10-30 23:24:59.419100

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '889c8e4f8974'
down_revision = '20f4c8ae647c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('evaluations', sa.Column('data', postgresql.JSONB(), nullable=False))
    op.add_column('evaluations', sa.Column('version', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('evaluations', 'version')
    op.drop_column('evaluations', 'data')
