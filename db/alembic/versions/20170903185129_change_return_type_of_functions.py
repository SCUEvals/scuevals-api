"""change return type of functions

Revision ID: d2d2f196738b
Revises: 
Create Date: 2017-09-03 16:13:31.799366

"""
from alembic import op
import sqlalchemy as sa
from db.alembic.helper import execute_file

# revision identifiers, used by Alembic.


revision = 'd2d2f196738b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('drop function if exists update_departments(jsonb)')
    execute_file('db/functions/update_departments.sql')


def downgrade():
    pass
