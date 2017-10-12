"""Added Majors

Revision ID: 8e798b2a2354
Revises: 2c9a3471c439
Create Date: 2017-10-12 11:14:24.033124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e798b2a2354'
down_revision = '2c9a3471c439'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'majors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text, nullable=False, unique=True)
    )

    op.create_table(
        'student_major',
        sa.Column('student_id', sa.Integer, sa.ForeignKey('students.id')),
        sa.Column('major_id', sa.Integer, sa.ForeignKey('majors.id')),
        sa.UniqueConstraint('student_id', 'major_id')
    )


def downgrade():
    op.drop_table('student_major')
    op.drop_table('majors')
