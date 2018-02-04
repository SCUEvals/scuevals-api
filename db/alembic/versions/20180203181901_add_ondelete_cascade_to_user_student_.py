"""Add ondelete cascade to user student and user role

Revision ID: d6947fa132f3
Revises: 3ba889712e73
Create Date: 2018-02-03 18:19:01.563647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6947fa132f3'
down_revision = '3ba889712e73'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fk_students_id_users', 'students', type_='foreignkey')
    op.create_foreign_key(op.f('fk_students_id_users'), 'students', 'users', ['id'], ['id'], ondelete='cascade')
    op.drop_constraint('fk_user_role_student_id', 'user_role', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_user_role_user_id_users'), 'user_role', 'users', ['user_id'], ['id'], ondelete='cascade'
    )


def downgrade():
    op.drop_constraint(op.f('fk_user_role_user_id_users'), 'user_role', type_='foreignkey')
    op.create_foreign_key('fk_user_role_student_id', 'user_role', 'users', ['user_id'], ['id'])
    op.drop_constraint(op.f('fk_students_id_users'), 'students', type_='foreignkey')
    op.create_foreign_key('fk_students_id_users', 'students', 'users', ['id'], ['id'])
