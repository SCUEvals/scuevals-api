create or replace function update_departments(_university_id numeric, _json jsonb)
  returns numeric as $func$
declare
  _s_id   numeric;
  _count  numeric := 0;
  _abbr   varchar;
  _name   varchar;
  _school varchar;
begin
  for _abbr, _name, _school in
  select
    department ->> 'value' as _abbr,
    (regexp_matches(department ->> 'label', '.+(?=\s\()')) [1] as _name,
    department ->> 'school' as _school
  from jsonb_array_elements(_json -> 'departments') department
  loop
    -- get the school id
    select id
    into _s_id
    from schools
    where abbreviation = _school and university_id = _university_id;

    -- upsert the department
    insert into departments (abbreviation, name, school_id) values (_abbr, _name, _s_id)
    on conflict on constraint uq_departments_abbreviation do
    update set name = _name where departments.abbreviation = _abbr and departments.school_id = _s_id;

    _count = _count + 1;

  end loop;

  return _count;
end;
$func$ language plpgsql;