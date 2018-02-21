"""Update roles for existing users

Revision ID: bd5bc783b2c0
Revises: faef4f4864c8
Create Date: 2018-02-19 20:45:36.235441

"""

from alembic import op
from sqlalchemy.orm.session import Session
from datetime import timedelta
from scuevals_api.models import Role, Quarter


# revision identifiers, used by Alembic.
revision = 'bd5bc783b2c0'
down_revision = 'faef4f4864c8'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('students', 'read_access_until', nullable=True)

    session = Session(bind=op.get_bind())
    sread = session.query(Role).get(Role.StudentRead)
    swrite = session.query(Role).get(Role.StudentWrite)

    # select the period of the current quarter
    cur_quarter_period = session.query(Quarter.period).filter_by(current=True).one()[0]

    # add the writing permission to everyone who currently has the reading permission
    # allow them to keep the reading permission until the last day of the current quarter
    for user in sread.users:
        user.read_access_until = cur_quarter_period.upper + timedelta(days=1)
        user.roles.append(swrite)

    # set the read_access_until to null for all incomplete students
    incomp = session.query(Role).get(Role.Incomplete)
    for user in incomp.users:
        user.read_access_until = None

    session.commit()


def downgrade():
    pass
