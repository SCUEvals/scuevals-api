"""Add reasons

Revision ID: aa99fce53c95
Revises: a6c8efa2274c
Create Date: 2018-03-18 23:44:37.587021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa99fce53c95'
down_revision = 'a6c8efa2274c'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("""
    insert into reasons (id, name) values
    (0, 'Other'),
    (1, 'Spam'), 
    (2, 'Offensive'), 
    (3, 'SensitiveInfo');
    """)


def downgrade():
    pass
