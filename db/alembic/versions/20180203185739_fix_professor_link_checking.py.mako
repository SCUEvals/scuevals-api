"""Fix professor link checking

Revision ID: 475a581f697a
Revises: d6947fa132f3
Create Date: 2018-02-03 18:57:39.936014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '475a581f697a'
down_revision = 'd6947fa132f3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""<%include file="triggers/professors.sql" />"""))


def downgrade():
    pass
