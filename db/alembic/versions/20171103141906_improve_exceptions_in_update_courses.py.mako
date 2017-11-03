"""Improve exceptions in update_courses

Revision ID: 0e1d4f004dde
Revises: 8c0d5ff8631d
Create Date: 2017-11-03 14:19:06.052853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e1d4f004dde'
down_revision = '8c0d5ff8631d'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('drop function if exists update_courses(jsonb)')
    conn.execute(sa.text("""<%include file="functions/update_courses.sql" />"""))


def downgrade():
    pass
