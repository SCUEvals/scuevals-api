"""Make student email mandatory

Revision ID: cff838c13b32
Revises: 0075b051bc84
Create Date: 2017-10-13 16:17:47.225028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cff838c13b32'
down_revision = '0075b051bc84'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('students', 'email',
                    existing_type=sa.TEXT(),
                    nullable=False)


def downgrade():
    op.alter_column('students', 'email',
                    existing_type=sa.TEXT(),
                    nullable=True)
