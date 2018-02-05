"""Add datetime column to vote

Revision ID: 9b53dd8832b6
Revises: 5debb667e48b
Create Date: 2018-02-05 11:27:10.742269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b53dd8832b6'
down_revision = '5debb667e48b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('votes',
                  sa.Column('time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))


def downgrade():
    op.drop_column('votes', 'time')
