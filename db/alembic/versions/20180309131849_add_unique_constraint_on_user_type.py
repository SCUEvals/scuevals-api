"""Add unique constraint on user type

Revision ID: 5e1a65b96e72
Revises: 75b3de1db013
Create Date: 2018-03-09 13:18:49.237762

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5e1a65b96e72'
down_revision = '75b3de1db013'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(op.f('uq_official_user_type_email'), 'official_user_type',
                                ['email', 'type', 'university_id'])


def downgrade():
    op.drop_constraint(op.f('uq_official_user_type_email'), 'official_user_type', type='unique')
