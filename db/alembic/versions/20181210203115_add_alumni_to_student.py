"""Add alumni to Student

Revision ID: 9701c694bd57
Revises: ea18d1a55b5f
Create Date: 2018-12-10 20:31:15.022743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9701c694bd57'
down_revision = 'ea18d1a55b5f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('students', sa.Column('alumni', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('students', 'alumni')
