"""update db functions

Revision ID: 8a786f9bf241
Revises: 0c2ff8b95c98
Create Date: 2017-09-27 00:11:13.429144

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision = '8a786f9bf241'
down_revision = '0c2ff8b95c98'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('drop function if exists update_courses(numeric, jsonb)')

    conn.execute(sa.text("""<%include file="functions/update_departments.sql" />"""))
    conn.execute(sa.text("""<%include file="functions/update_courses.sql" />"""))


def downgrade():
    pass
