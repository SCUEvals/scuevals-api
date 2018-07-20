"""Add Official User Type Permission

Revision ID: f09a839a633e
Revises: c7b39cfb1e92
Create Date: 2018-07-20 12:36:14.894477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f09a839a633e'
down_revision = 'c7b39cfb1e92'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("""insert into permissions (id, name) values(103, 'UpdateOfficialUserTypes')""")


def downgrade():
    conn = op.get_bind()
    conn.execute("""delete from permissions where id=103""")
