"""Fix update_courses

Revision ID: 7004250e3ef5
Revises: 8a786f9bf241
Create Date: 2017-09-27 09:34:46.069174

"""
from alembic import op
import sqlalchemy as sa
from db.alembic.helper import execute_file

# revision identifiers, used by Alembic.

revision = '7004250e3ef5'
down_revision = '8a786f9bf241'
branch_labels = None
depends_on = None


def upgrade():
    execute_file('db/functions/update_courses.sql')


def downgrade():
    pass
