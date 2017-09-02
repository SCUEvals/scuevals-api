create or replace function update_departments(_json jsonb)
  returns void as $func$
declare
  _s_id   numeric;
  _d_id   numeric;
  _abbr   varchar;
  _name   varchar;
  _school varchar;
begin
  for _abbr, _name, _school in
  select
    department ->> 'value' as _abbr,
    (regexp_matches(department ->> 'label', '.+(?=\()')) [1] as _name,
    department ->> 'school' as _school
  from jsonb_array_elements(_json -> 'results') department
  loop
    -- get the school id
    select school.id
    into _s_id
    from school
    where abbreviation = _school;

    -- get the department id if it exists
    select id
    into _d_id
    from department
    where school_id = _s_id and abbreviation = _abbr;

    -- if department does not exist, create it
    if _d_id is null
    then
      insert into department (abbreviation, name, school_id) values (_abbr, _name, _s_id);
    end if;

  end loop;
end;
$func$ language plpgsql;