"""Update roles for existing users

Revision ID: bd5bc783b2c0
Revises: faef4f4864c8
Create Date: 2018-02-19 20:45:36.235441

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bd5bc783b2c0'
down_revision = 'faef4f4864c8'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('students', 'read_access_until', nullable=True)

    conn = op.get_bind()

    # add the writing permission to everyone who currently has the reading permission
    # allow them to keep the reading permission until the last day of the current quarter
    conn.execute("""
update students
set read_access_until = (select (upper(period) + interval '35 hours') from quarters where current = true)
where id in (select id from user_role where role_id = 1)
                 """)

    conn.execute("""
insert into user_role (user_id, role_id)
select user_id, 2 from user_role where role_id = 1
                 """)

    # set the read_access_until to null for all incomplete students
    conn.execute("""
update students set read_access_until = null
where id in (select user_id from user_role where role_id = 0)
                 """)


def downgrade():
    pass
