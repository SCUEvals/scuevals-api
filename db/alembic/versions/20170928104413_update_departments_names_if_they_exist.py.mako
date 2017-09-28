"""Update departments names if they exist

Revision ID: 15bc0e6fa7a0
Revises: 7004250e3ef5
Create Date: 2017-09-28 10:44:13.788317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15bc0e6fa7a0'
down_revision = '7004250e3ef5'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""<%include file="functions/update_departments.sql" />"""))


def downgrade():
    pass
