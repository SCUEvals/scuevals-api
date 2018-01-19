"""Add user-professor relationship constraints

Revision ID: 745eb5d53a01
Revises: f402330a95fb
Create Date: 2018-01-18 17:45:09.742569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '745eb5d53a01'
down_revision = 'f402330a95fb'
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

  if (tg_op != 'DELETE' and new.user_id is null and old.user_id is not null) then
    -- unlinking
    if (select "type" from users where id = old.user_id) = 'p' then
      raise exception 'user type is "p"';
    end if;
  end if;

  return new;
end;
$trig$ language plpgsql;

create constraint trigger professor_user_link_trig after insert or update of user_id or delete
  on professors
  deferrable initially deferred
for each row
execute procedure professor_user_link_check();"""))
    conn.execute(sa.text("""create or replace function user_professor_link_check()
  returns trigger as $trig$
begin
  if (tg_op = 'INSERT' and new.type != 'p') or (tg_op = 'UPDATE' and old.type != 'p' and new.type != 'p') then
    return new;
  end if;

  if (new.type = 'p') then
    -- linking
    if not (select exists(select 1 from professors where user_id = new.id)) then
      raise exception 'no professor is linked to user with id "%"', new.id;
    end if;
  else
    -- unlinking
    if (select exists(select 1 from professors where user_id = new.id)) then
      raise exception 'a professor is linked to user with id "%"', new.id;
    end if;
  end if;

  return new;
end;
$trig$ language plpgsql;

create constraint trigger user_professor_link_trig after insert or update of "type"
  on users
  deferrable initially deferred
for each row
execute procedure user_professor_link_check();"""))


def downgrade():
    pass
