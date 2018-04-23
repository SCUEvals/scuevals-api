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
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('majors', sa.Column('department_id', sa.Integer(), nullable=True))
    op.drop_constraint('majors_university_id_fkey', 'majors', type_='foreignkey')
    op.create_foreign_key(op.f('fk_majors_department_id_departments'),
                          'majors', 'departments', ['department_id'], ['id'])
    op.drop_column('majors', 'university_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('majors', sa.Column('university_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(op.f('fk_majors_department_id_departments'), 'majors', type_='foreignkey')
    op.create_foreign_key('majors_university_id_fkey', 'majors', 'universities', ['university_id'], ['id'])
    op.drop_column('majors', 'department_id')
    # ### end Alembic commands ###
