"""Connect majors to departments

Revision ID: b1afd1844ad0
Revises: 712c698d15b5
Create Date: 2018-04-20 15:52:21.583009

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b1afd1844ad0'
down_revision = '712c698d15b5'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('majors_university_id_fkey', 'majors', type_='foreignkey')
    op.drop_column('majors', 'university_id')

    op.create_table(
        'department_major',
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('major_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'],
                                name=op.f('fk_department_major_department_id_departments'),
                                ondelete='cascade'),
        sa.ForeignKeyConstraint(['major_id'], ['majors.id'],
                                name=op.f('fk_department_major_major_id_majors'),
                                ondelete='cascade'),
        sa.UniqueConstraint('department_id', 'major_id', name=op.f('uq_department_major_department_id'))
    )

    op.drop_constraint('fk_api_key_permission_permission_id_permissions', 'api_key_permission', type_='foreignkey')
    op.create_foreign_key(op.f('fk_api_key_permission_permission_id_permissions'), 'api_key_permission', 'permissions',
                          ['permission_id'], ['id'], ondelete='cascade')
    op.drop_constraint('fk_flag_reason_reason_id_reasons', 'flag_reason', type_='foreignkey')
    op.create_foreign_key(op.f('fk_flag_reason_reason_id_reasons'), 'flag_reason', 'reasons', ['reason_id'], ['id'],
                          ondelete='cascade')
    op.drop_constraint('section_professor_professor_id_fkey', 'section_professor', type_='foreignkey')
    op.create_foreign_key(op.f('fk_section_professor_professor_id_professors'), 'section_professor', 'professors',
                          ['professor_id'], ['id'], ondelete='cascade')
    op.drop_constraint('student_major_major_id_fkey', 'student_major', type_='foreignkey')
    op.create_foreign_key(op.f('fk_student_major_major_id_majors'), 'student_major', 'majors', ['major_id'], ['id'],
                          ondelete='cascade')
    op.drop_constraint('fk_user_permission_permission_id', 'user_permission', type_='foreignkey')
    op.create_foreign_key(op.f('fk_user_permission_permission_id_permissions'), 'user_permission', 'permissions',
                          ['permission_id'], ['id'], ondelete='cascade')


def downgrade():
    op.add_column('majors', sa.Column('university_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('majors_university_id_fkey', 'majors', 'universities', ['university_id'], ['id'])

    op.drop_constraint(op.f('fk_user_permission_permission_id_permissions'), 'user_permission', type_='foreignkey')
    op.create_foreign_key('fk_user_permission_permission_id', 'user_permission', 'permissions', ['permission_id'],
                          ['id'])
    op.drop_constraint(op.f('fk_student_major_major_id_majors'), 'student_major', type_='foreignkey')
    op.create_foreign_key('student_major_major_id_fkey', 'student_major', 'majors', ['major_id'], ['id'])
    op.drop_constraint(op.f('fk_section_professor_professor_id_professors'), 'section_professor', type_='foreignkey')
    op.create_foreign_key('section_professor_professor_id_fkey', 'section_professor', 'professors', ['professor_id'],
                          ['id'])
    op.drop_constraint(op.f('fk_flag_reason_reason_id_reasons'), 'flag_reason', type_='foreignkey')
    op.create_foreign_key('fk_flag_reason_reason_id_reasons', 'flag_reason', 'reasons', ['reason_id'], ['id'])
    op.drop_constraint(op.f('fk_api_key_permission_permission_id_permissions'), 'api_key_permission',
                       type_='foreignkey')
    op.create_foreign_key('fk_api_key_permission_permission_id_permissions', 'api_key_permission', 'permissions',
                          ['permission_id'], ['id'])
    op.drop_table('department_major')
