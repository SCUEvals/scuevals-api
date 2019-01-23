"""Remove quarter current column

Revision ID: 64a9e1dbdd68
Revises: c7b39cfb1e92
Create Date: 2018-05-09 00:09:08.376655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64a9e1dbdd68'
down_revision = 'c7b39cfb1e92'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('uq_quarters_current', table_name='quarters')
    op.drop_column('quarters', 'current')


def downgrade():
    op.create_unique_constraint('uq_student_major_student_id_major_id_index', 'student_major',
                                ['student_id', 'major_id', 'index'])
    op.add_column('quarters', sa.Column('current', sa.BOOLEAN(), autoincrement=False, nullable=True))
