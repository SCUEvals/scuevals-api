"""Fix professor names in update_courses

Revision ID: f74a7a82b8e0
Revises: 2110d273e2b3
Create Date: 2018-01-14 18:04:05.998412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f74a7a82b8e0'
down_revision = '2110d273e2b3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('drop function if exists update_courses(jsonb)')
    conn.execute(sa.text("""<%include file="functions/update_courses.sql" />"""))


def downgrade():
    pass
