"""Add picture to student

Revision ID: c7b5446dc1b4
Revises: cff838c13b32
Create Date: 2017-10-15 21:50:54.472673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7b5446dc1b4'
down_revision = 'cff838c13b32'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'students',
        sa.Column('picture', sa.Text)
    )


def downgrade():
    op.drop_column('students', 'picture')
