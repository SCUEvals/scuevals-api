"""Add evaluation data

Revision ID: fba9c57320a8
Revises: 13604c9c2473
Create Date: 2017-11-02 00:50:14.085493

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fba9c57320a8'
down_revision = '13604c9c2473'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('evaluations', sa.Column('professor_id', sa.Integer(), nullable=False))
    op.add_column('evaluations', sa.Column('version', sa.Integer(), nullable=False))
    op.add_column('evaluations', sa.Column('data', postgresql.JSONB(), nullable=False))

    op.drop_constraint('uq_evaluations_student_id', 'evaluations', type_='unique')
    op.create_unique_constraint(op.f('uq_evaluations_student_id'), 'evaluations', ['student_id', 'professor_id', 'section_id'])
    op.create_foreign_key(op.f('fk_evaluations_professor_id_professors'), 'evaluations', 'professors', ['professor_id'], ['id'])


def downgrade():
    op.drop_constraint(op.f('fk_evaluations_professor_id_professors'), 'evaluations', type_='foreignkey')
    op.drop_constraint(op.f('uq_evaluations_student_id'), 'evaluations', type_='unique')
    op.create_unique_constraint('uq_evaluations_student_id', 'evaluations', ['student_id', 'section_id'])
    op.drop_column('evaluations', 'version')
    op.drop_column('evaluations', 'professor_id')
    op.drop_column('evaluations', 'data')
