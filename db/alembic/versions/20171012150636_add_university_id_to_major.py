"""Add university id to Major

Revision ID: 3c13dfa66a11
Revises: 8e798b2a2354
Create Date: 2017-10-12 15:06:36.201364

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3c13dfa66a11'
down_revision = '8e798b2a2354'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'majors',
        sa.Column('university_id', sa.Integer, sa.ForeignKey('universities.id'), nullable=False)
    )


def downgrade():
    op.drop_column('majors', 'university_id')
