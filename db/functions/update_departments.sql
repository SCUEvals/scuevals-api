create or replace function update_departments(_university_id numeric, _json jsonb)
  returns numeric as $func$
declare
  _s_id   numeric;
  _d_id   numeric;
  _count  numeric := 0;
  _abbr   varchar;
  _name   varchar;
  _school varchar;
begin
  for _abbr, _name, _school in
  select
    department ->> 'value' as _abbr,
    (regexp_matches(department ->> 'label', '.+(?=\()')) [1] as _name,
    department ->> 'school' as _school
  from jsonb_array_elements(_json -> 'departments') department
  loop
    -- get the school id
    select id
    into _s_id
    from schools
    where abbreviation = _school and university_id = _university_id;

    -- get the department id if it exists
    select id
    into _d_id
    from departments
    where school_id = _s_id and abbreviation = _abbr;

    -- if department does not exist, create it
    if _d_id is null
    then
      insert into departments (abbreviation, name, school_id) values (_abbr, _name, _s_id);
    end if;

    _count = _count + 1;

  end loop;

  return _count;
end;
$func$ language plpgsql;