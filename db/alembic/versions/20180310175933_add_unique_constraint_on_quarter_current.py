"""Add unique constraint on quarter current

Revision ID: 7fce5e7f49af
Revises: 5e1a65b96e72
Create Date: 2018-03-10 17:59:33.547817

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fce5e7f49af'
down_revision = '5e1a65b96e72'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('uq_quarters_current', 'quarters', ['current'], unique=True, postgresql_where=sa.text('current'))


def downgrade():
    op.drop_index('uq_quarters_current', table_name='quarters')
