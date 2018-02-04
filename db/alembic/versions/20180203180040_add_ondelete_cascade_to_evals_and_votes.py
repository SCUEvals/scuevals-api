"""Add ondelete cascade to evals and votes

Revision ID: 6137505449d2
Revises: 352f2fdca283
Create Date: 2018-02-03 18:00:40.384570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6137505449d2'
down_revision = '352f2fdca283'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fk_evaluations_student_id_students', 'evaluations', type_='foreignkey')

    op.create_foreign_key(
        op.f('fk_evaluations_student_id_students'), 'evaluations', 'students',
        ['student_id'], ['id'], ondelete='cascade'
    )

    op.drop_constraint('fk_votes_student_id_students', 'votes', type_='foreignkey')
    op.drop_constraint('fk_votes_evaluation_id_evaluations', 'votes', type_='foreignkey')

    op.create_foreign_key(
        op.f('fk_votes_student_id_students'), 'votes', 'students', ['student_id'], ['id'], ondelete='cascade'
    )

    op.create_foreign_key(
        op.f('fk_votes_evaluation_id_evaluations'), 'votes', 'evaluations',
        ['evaluation_id'], ['id'], ondelete='cascade'
    )


def downgrade():
    op.drop_constraint(op.f('fk_votes_evaluation_id_evaluations'), 'votes', type_='foreignkey')
    op.drop_constraint(op.f('fk_votes_student_id_students'), 'votes', type_='foreignkey')
    op.create_foreign_key('fk_votes_evaluation_id_evaluations', 'votes', 'evaluations', ['evaluation_id'], ['id'])
    op.create_foreign_key('fk_votes_student_id_students', 'votes', 'students', ['student_id'], ['id'])
    op.drop_constraint(op.f('fk_evaluations_student_id_students'), 'evaluations', type_='foreignkey')
    op.create_foreign_key('fk_evaluations_student_id_students', 'evaluations', 'students', ['student_id'], ['id'])
