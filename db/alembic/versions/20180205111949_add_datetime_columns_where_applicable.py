"""Add datetime columns where applicable

Revision ID: 5debb667e48b
Revises: 475a581f697a
Create Date: 2018-02-05 11:19:49.072723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5debb667e48b'
down_revision = '475a581f697a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('evaluations',
                  sa.Column('post_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('users',
                  sa.Column('signup_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))


def downgrade():
    op.drop_column('users', 'signup_time')
    op.drop_column('evaluations', 'post_time')
