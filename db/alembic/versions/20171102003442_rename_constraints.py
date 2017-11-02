"""Add evaluation data

Revision ID: 13604c9c2473
Revises: 20f4c8ae647c
Create Date: 2017-11-02 00:34:42.148237

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '13604c9c2473'
down_revision = '20f4c8ae647c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(op.f('uq_api_keys_key'), 'api_keys', ['key'])
    op.drop_constraint('api_keys_key_key', 'api_keys', type_='unique')
    op.create_unique_constraint(op.f('uq_courses_department_id'), 'courses', ['department_id', 'number'])
    op.drop_constraint('uix_course', 'courses', type_='unique')
    op.create_unique_constraint(op.f('uq_departments_abbreviation'), 'departments', ['abbreviation', 'school_id'])
    op.drop_constraint('departments_abbreviation_school_id_key', 'departments', type_='unique')
    op.create_unique_constraint(op.f('uq_evaluations_student_id'), 'evaluations', ['student_id', 'section_id'])
    op.drop_constraint('evaluations_student_id_section_id_key', 'evaluations', type_='unique')
    op.create_unique_constraint(op.f('uq_majors_name'), 'majors', ['name'])
    op.drop_constraint('majors_name_key', 'majors', type_='unique')
    op.create_unique_constraint(op.f('uq_quarters_year'), 'quarters', ['year', 'name', 'university_id'])
    op.drop_constraint('quarters_year_name_university_id_key', 'quarters', type_='unique')
    op.create_unique_constraint(op.f('uq_roles_name'), 'roles', ['name'])
    op.drop_constraint('roles_name_key', 'roles', type_='unique')
    op.create_unique_constraint(op.f('uq_schools_abbreviation'), 'schools', ['abbreviation'])
    op.drop_constraint('schools_abbreviation_key', 'schools', type_='unique')
    op.create_unique_constraint(op.f('uq_section_professor_section_id'), 'section_professor', ['section_id', 'professor_id'])
    op.drop_constraint('section_professor_section_id_professor_id_key', 'section_professor', type_='unique')
    op.create_unique_constraint(op.f('uq_sections_quarter_id'), 'sections', ['quarter_id', 'course_id'])
    op.drop_constraint('sections_quarter_id_course_id_key', 'sections', type_='unique')
    op.create_unique_constraint(op.f('uq_student_major_student_id'), 'student_major', ['student_id', 'major_id'])
    op.drop_constraint('student_major_student_id_major_id_key', 'student_major', type_='unique')
    op.create_unique_constraint(op.f('uq_student_role_student_id'), 'student_role', ['student_id', 'role_id'])
    op.drop_constraint('student_role_student_id_role_id_key', 'student_role', type_='unique')
    op.create_unique_constraint(op.f('uq_students_email'), 'students', ['email'])
    op.drop_constraint('students_email_key', 'students', type_='unique')
    op.create_unique_constraint(op.f('uq_universities_abbreviation'), 'universities', ['abbreviation'])
    op.drop_constraint('universities_abbreviation_key', 'universities', type_='unique')


def downgrade():
    op.create_unique_constraint('universities_abbreviation_key', 'universities', ['abbreviation'])
    op.drop_constraint(op.f('uq_universities_abbreviation'), 'universities', type_='unique')
    op.create_unique_constraint('students_email_key', 'students', ['email'])
    op.drop_constraint(op.f('uq_students_email'), 'students', type_='unique')
    op.create_unique_constraint('student_role_student_id_role_id_key', 'student_role', ['student_id', 'role_id'])
    op.drop_constraint(op.f('uq_student_role_student_id'), 'student_role', type_='unique')
    op.create_unique_constraint('student_major_student_id_major_id_key', 'student_major', ['student_id', 'major_id'])
    op.drop_constraint(op.f('uq_student_major_student_id'), 'student_major', type_='unique')
    op.create_unique_constraint('sections_quarter_id_course_id_key', 'sections', ['quarter_id', 'course_id'])
    op.drop_constraint(op.f('uq_sections_quarter_id'), 'sections', type_='unique')
    op.create_unique_constraint('section_professor_section_id_professor_id_key', 'section_professor', ['section_id', 'professor_id'])
    op.drop_constraint(op.f('uq_section_professor_section_id'), 'section_professor', type_='unique')
    op.create_unique_constraint('schools_abbreviation_key', 'schools', ['abbreviation'])
    op.drop_constraint(op.f('uq_schools_abbreviation'), 'schools', type_='unique')
    op.create_unique_constraint('roles_name_key', 'roles', ['name'])
    op.drop_constraint(op.f('uq_roles_name'), 'roles', type_='unique')
    op.create_unique_constraint('quarters_year_name_university_id_key', 'quarters', ['year', 'name', 'university_id'])
    op.drop_constraint(op.f('uq_quarters_year'), 'quarters', type_='unique')
    op.create_unique_constraint('majors_name_key', 'majors', ['name'])
    op.drop_constraint(op.f('uq_majors_name'), 'majors', type_='unique')
    op.create_unique_constraint('evaluations_student_id_section_id_key', 'evaluations', ['student_id', 'section_id'])
    op.drop_constraint(op.f('uq_evaluations_student_id'), 'evaluations', type_='unique')
    op.create_unique_constraint('departments_abbreviation_school_id_key', 'departments', ['abbreviation', 'school_id'])
    op.drop_constraint(op.f('uq_departments_abbreviation'), 'departments', type_='unique')
    op.create_unique_constraint('uix_course', 'courses', ['department_id', 'number'])
    op.drop_constraint(op.f('uq_courses_department_id'), 'courses', type_='unique')
    op.create_unique_constraint('api_keys_key_key', 'api_keys', ['key'])
    op.drop_constraint(op.f('uq_api_keys_key'), 'api_keys', type_='unique')
