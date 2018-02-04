"""Add ondelete cascade to student majors

Revision ID: 3ba889712e73
Revises: 6137505449d2
Create Date: 2018-02-03 18:10:47.675066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ba889712e73'
down_revision = '6137505449d2'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fk_student_major_student_id_students', 'student_major', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_student_major_student_id_students'), 'student_major', 'students',
        ['student_id'], ['id'], ondelete='cascade'
    )


def downgrade():
    op.drop_constraint(op.f('fk_student_major_student_id_students'), 'student_major', type_='foreignkey')
    op.create_foreign_key('fk_student_major_student_id_students', 'student_major', 'students', ['student_id'], ['id'])
