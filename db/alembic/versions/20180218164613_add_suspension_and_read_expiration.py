"""Add suspension and read expiration

Revision ID: faef4f4864c8
Revises: 81e54da1026b
Create Date: 2018-02-18 16:46:13.708454

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from scuevals_api.models import Role


# revision identifiers, used by Alembic.
revision = 'faef4f4864c8'
down_revision = '81e54da1026b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('students', sa.Column(
        'read_access_until', sa.DateTime(timezone=True), nullable=False,
        server_default=sa.text("now() + interval '180 days'")
    ))

    op.alter_column('students', 'read_access_until', server_default=None)

    op.add_column('users', sa.Column('suspended_until', sa.DateTime(timezone=True), nullable=True))

    session = Session(bind=op.get_bind())
    sread = session.query(Role).get(1)
    sread.name = 'StudentRead'

    swrite = Role(id=Role.StudentWrite, name='StudentWrite')
    session.add(swrite)

    session.commit()


def downgrade():
    pass
