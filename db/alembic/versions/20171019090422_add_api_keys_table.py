"""Add API Keys Table

Revision ID: 20f4c8ae647c
Revises: a055c705e071
Create Date: 2017-10-19 09:04:22.425249

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20f4c8ae647c'
down_revision = 'a055c705e071'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('key', sa.Text, nullable=False, unique=True),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('university_id', sa.Integer, sa.ForeignKey('universities.id'), nullable=False)
    )

    roles = sa.table('roles', sa.Column('id'), sa.Column('name'))

    op.bulk_insert(
        roles,
        [
            {'id': 20, 'name': 'API Key'}
        ]
    )


def downgrade():
    op.drop_table('api_keys')
