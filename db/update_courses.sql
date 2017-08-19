create or replace function update_courses(_quarter numeric, _json jsonb)
  returns void as $func$
declare
  _d_id       numeric;
  _c_id       numeric;
  _department varchar;
  _number     varchar;

begin
  for _department, _number in
  select
    split_part(course ->> 'value', ' ', 1) as _department,
    split_part(course ->> 'value', ' ', 2) as _number
  from jsonb_array_elements(_json -> 'results') course
  loop
    -- get the department id
    select department.id
    into _d_id
    from department
    where abbreviation = _department;

    -- get the course id if it exists
    select id
    into _c_id
    from course
    where department_id = _d_id and number = _number;

    -- if the course does not exist, create it
    if _c_id is null
    then
      insert into course (department_id, number) values (_d_id, _number)
      returning id
        into _c_id;
    end if;

    -- if the course is not yet listed under the specified quarter, list it
    if not exists(select 1
                  from quarter_course
                  where course_id = _c_id and quarter_id = _quarter)
    then
      insert into quarter_course (quarter_id, course_id) values (_quarter, _c_id);
    end if;

  end loop;

end;
$func$ language plpgsql;