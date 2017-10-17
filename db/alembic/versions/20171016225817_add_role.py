"""Add Role

Revision ID: a055c705e071
Revises: c7b5446dc1b4
Create Date: 2017-10-16 22:58:17.355362

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a055c705e071'
down_revision = 'c7b5446dc1b4'
branch_labels = None
depends_on = None


def upgrade():
    roles = op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text, nullable=False, unique=True)
    )

    op.create_table(
        'student_role',
        sa.Column('student_id', sa.Integer, sa.ForeignKey('students.id')),
        sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id')),
        sa.UniqueConstraint('student_id', 'role_id')
    )

    op.bulk_insert(
        roles,
        [
            {'id': 0, 'name': 'Incomplete'},
            {'id': 1, 'name': 'Student'},
            {'id': 10, 'name': 'Administrator'}
        ]
    )


def downgrade():
    op.drop_table('student_role')
    op.drop_table('roles')
