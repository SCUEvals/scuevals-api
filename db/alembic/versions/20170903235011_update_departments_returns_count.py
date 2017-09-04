"""update_departments returns count

Revision ID: 0c2ff8b95c98
Revises: d2d2f196738b
Create Date: 2017-09-03 23:50:11.640905

"""
from alembic import op
import sqlalchemy as sa
from db.alembic.helper import execute_file

# revision identifiers, used by Alembic.

revision = '0c2ff8b95c98'
down_revision = 'd2d2f196738b'
branch_labels = None
depends_on = None


def upgrade():
    execute_file('db/functions/update_departments.sql')


def downgrade():
    pass
