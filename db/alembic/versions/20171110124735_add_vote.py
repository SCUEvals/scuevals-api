"""Add Vote

Revision ID: 2110d273e2b3
Revises: 0e1d4f004dde
Create Date: 2017-11-10 12:47:35.238799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2110d273e2b3'
down_revision = '0e1d4f004dde'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('votes',
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('evaluation_id', sa.Integer(), nullable=False),
    sa.CheckConstraint('value != 0', name=op.f('ck_votes_non_zero_value')),
    sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'], name=op.f('fk_votes_evaluation_id_evaluations')),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_votes_student_id_students')),
    sa.PrimaryKeyConstraint('student_id', 'evaluation_id', name=op.f('pk_votes'))
    )


def downgrade():
    op.drop_table('votes')
