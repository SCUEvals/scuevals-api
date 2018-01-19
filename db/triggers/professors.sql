create or replace function professor_user_link_check()
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
execute procedure professor_user_link_check();