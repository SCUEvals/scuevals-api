"""Modify Student roles

Revision ID: 2c5034325ddf
Revises: faef4f4864c8
Create Date: 2018-02-15 12:10:50.604349

"""
from alembic import op
from sqlalchemy.orm.session import Session
from scuevals_api import db
from scuevals_api.models import Role


# revision identifiers, used by Alembic.


revision = '2c5034325ddf'
down_revision = 'faef4f4864c8'
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    sread = session.query(Role).get(1)
    sread.name = 'StudentRead'

    swrite = Role(id=Role.StudentWrite, name='StudentWrite')
    session.add(swrite)

    suspended = Role(id=Role.Suspended, name='Suspended')
    session.add(suspended)

    session.commit()


def downgrade():
    pass
