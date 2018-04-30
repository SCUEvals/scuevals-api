"""Add index to student_major

Revision ID: c7b39cfb1e92
Revises: b1afd1844ad0
Create Date: 2018-04-30 15:08:34.654224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7b39cfb1e92'
down_revision = 'b1afd1844ad0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('student_major', sa.Column('index', sa.Integer()))

    conn = op.get_bind()
    conn.execute("""
    update student_major
    set "index" = (sq.index-1)
    from
      (select
         student_id,
         major_id,
         row_number()
         over (partition by student_id ) as index
       from student_major) as sq
    where student_major.student_id=sq.student_id and student_major.major_id=sq.major_id;
    """)

    op.alter_column('student_major', 'index', nullable=False)
    op.drop_constraint('uq_student_major_student_id', 'student_major', type_='unique')
    op.create_unique_constraint(
        'uq_student_major_student_id_major_id_index', 'student_major', ['student_id', 'major_id', 'index']
    )


def downgrade():
    op.drop_constraint('uq_student_major_student_id_major_id_index', 'student_major', type_='unique')
    op.create_unique_constraint('uq_student_major_student_id', 'student_major', ['student_id', 'major_id'])
    op.drop_column('student_major', 'index')
