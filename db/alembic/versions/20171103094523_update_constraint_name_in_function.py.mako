"""Update constraint name in function

Revision ID: 8c0d5ff8631d
Revises: fba9c57320a8
Create Date: 2017-11-03 09:45:23.175072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c0d5ff8631d'
down_revision = 'fba9c57320a8'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('drop function if exists update_departments(jsonb)')
    conn.execute(sa.text("""<%include file="functions/update_departments.sql" />"""))


def downgrade():
    pass
