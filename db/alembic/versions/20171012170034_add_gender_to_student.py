"""Add gender to Student

Revision ID: 0075b051bc84
Revises: 3c13dfa66a11
Create Date: 2017-10-12 17:00:34.056860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import column

revision = '0075b051bc84'
down_revision = '3c13dfa66a11'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'students',
        sa.Column('gender', sa.String(1))
    )

    op.create_check_constraint('students_gender_check', 'students', column('gender').in_(['m', 'f', 'o']))


def downgrade():
    op.drop_constraint('students_gender_check', 'students')
    op.drop_column('students', 'gender')
