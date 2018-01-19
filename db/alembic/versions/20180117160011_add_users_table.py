"""Add users table

Revision ID: f402330a95fb
Revises: f74a7a82b8e0
Create Date: 2018-01-17 16:00:11.739010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f402330a95fb'
down_revision = 'f74a7a82b8e0'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    op.rename_table('students', 'users')

    op.create_table(
        'students',
        sa.Column('id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('graduation_year', sa.Integer),
        sa.Column('gender', sa.String(1))
    )

    conn.execute("""
insert into students (id, graduation_year, gender)
select id, graduation_year, gender from users;
    """)

    with op.batch_alter_table('users') as tbl:
        tbl.add_column(sa.Column('type', sa.String(1), server_default='u', nullable=False))
        tbl.drop_column('graduation_year')
        tbl.drop_column('gender')
        tbl.create_check_constraint('user_type', sa.column('type').in_(['s', 'p', 'u']))

    conn.execute("""update users set "type"='s';""")

    op.create_check_constraint('gender_check', 'students', sa.column('gender').in_(['m', 'f', 'o']))

    op.add_column('professors', sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), unique=True))

    op.rename_table('student_role', 'user_role')
    op.alter_column('user_role', 'student_id', new_column_name='user_id')
    op.drop_constraint('student_role_student_id_fkey', 'user_role')
    op.create_foreign_key('fk_user_role_student_id', 'user_role', 'users', ['user_id'], ['id'])

    conn.execute("""
alter table user_role rename constraint student_role_role_id_fkey to fk_user_role_role_id;
alter table user_role rename constraint uq_student_role_student_id to uq_user_role_user_id;
alter table users rename constraint students_pkey to pk_users;
alter table users rename constraint uq_students_email to uq_users_email;
alter table users rename constraint students_university_id_fkey to fk_users_university_id;
    """)

    op.drop_constraint('evaluations_student_id_fkey', 'evaluations', type_='foreignkey')
    op.create_foreign_key(op.f('fk_evaluations_student_id_students'), 'evaluations', 'students', ['student_id'], ['id'])
    op.drop_constraint('student_major_student_id_fkey', 'student_major', type_='foreignkey')
    op.create_foreign_key(op.f('fk_student_major_student_id_students'), 'student_major', 'students', ['student_id'], ['id'])
    op.drop_constraint('fk_votes_student_id_students', 'votes', type_='foreignkey')
    op.create_foreign_key(op.f('fk_votes_student_id_students'), 'votes', 'students', ['student_id'], ['id'])


def downgrade():
    pass
