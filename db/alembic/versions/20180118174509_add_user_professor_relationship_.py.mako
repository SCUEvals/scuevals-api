"""Add user-professor relationship constraints

Revision ID: 745eb5d53a01
Revises: f402330a95fb
Create Date: 2018-01-18 17:45:09.742569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '745eb5d53a01'
down_revision = 'f402330a95fb'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""<%include file="triggers/professors.sql" />"""))
    conn.execute(sa.text("""<%include file="triggers/users.sql" />"""))


def downgrade():
    pass
