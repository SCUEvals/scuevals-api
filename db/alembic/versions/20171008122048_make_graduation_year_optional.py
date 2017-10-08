"""Make graduation-year optional

Revision ID: 2c9a3471c439
Revises: 15bc0e6fa7a0
Create Date: 2017-10-08 12:20:48.969014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c9a3471c439'
down_revision = '15bc0e6fa7a0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('students', 'graduation_year',
                    existing_type=sa.INTEGER(),
                    nullable=True)


def downgrade():
    op.alter_column('students', 'graduation_year',
                    existing_type=sa.INTEGER(),
                    nullable=False)
