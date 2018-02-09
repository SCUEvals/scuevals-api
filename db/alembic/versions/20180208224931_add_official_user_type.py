"""Add Official User Type

Revision ID: 81e54da1026b
Revises: 3e029d844940
Create Date: 2018-02-08 22:49:31.597827

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '81e54da1026b'
down_revision = '3e029d844940'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('official_user_type',
                    sa.Column('email', sa.Text(), nullable=False),
                    sa.Column('type', sa.Text(), nullable=False),
                    sa.Column('university_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['university_id'], ['universities.id'],
                                            name=op.f('fk_official_user_type_university_id_universities')),
                    sa.PrimaryKeyConstraint('email', name=op.f('pk_official_user_type'))
                    )


def downgrade():
    op.drop_table('official_user_type')
