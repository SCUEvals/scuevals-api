"""Add eval display student info options

Revision ID: 352f2fdca283
Revises: 745eb5d53a01
Create Date: 2018-01-24 10:53:05.437076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '352f2fdca283'
down_revision = '745eb5d53a01'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('evaluations', sa.Column('display_grad_year', sa.Boolean(), server_default='t', nullable=False))
    op.add_column('evaluations', sa.Column('display_majors', sa.Boolean(), server_default='t', nullable=False))


def downgrade():
    op.drop_column('evaluations', 'display_majors')
    op.drop_column('evaluations', 'display_grad_year')
