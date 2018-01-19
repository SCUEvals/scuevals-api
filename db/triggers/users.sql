create or replace function user_professor_link_check()
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
execute procedure user_professor_link_check();