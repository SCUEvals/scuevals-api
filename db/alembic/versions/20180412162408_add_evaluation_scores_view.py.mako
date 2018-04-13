"""Add evaluation_scores view

Revision ID: 712c698d15b5
Revises: aa99fce53c95
Create Date: 2018-04-12 16:24:08.801361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '712c698d15b5'
down_revision = 'aa99fce53c95'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    conn.execute(sa.text("""<%include file="views/evaluation_scores.sql" />"""))


def downgrade():
    pass
