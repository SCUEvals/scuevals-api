"""Fix professor link checking

Revision ID: 475a581f697a
Revises: d6947fa132f3
Create Date: 2018-02-03 18:57:39.936014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '475a581f697a'
down_revision = 'd6947fa132f3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""create or replace function professor_user_link_check()
  returns trigger as $trig$
begin
  if tg_op = 'DELETE' and old.user_id is not null then
    if (select "type" from users where id = old.user_id) = 'p' then
      raise exception 'user type is "p"';
    end if;
  end if;

  if (tg_op != 'DELETE' and new.user_id is not null and old.user_id is null) then
    -- linking
    if (select "type" from users where id = new.user_id) != 'p' then
      raise exception 'user type is not "p"';
    end if;
  end if;

  if (tg_op = 'UPDATE' and new.user_id is null and old.user_id is not null) then
    -- unlinking
    if (select "type" from users where id = old.user_id) = 'p' then
      raise exception 'user type is "p"';
    end if;
  end if;

  return new;
end;
$trig$ language plpgsql;
    """))


def downgrade():
    pass
