"""Fix update_courses

Revision ID: 7004250e3ef5
Revises: 8a786f9bf241
Create Date: 2017-09-27 09:34:46.069174

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision = '7004250e3ef5'
down_revision = '8a786f9bf241'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""create or replace function update_courses(_university_id numeric, _json jsonb)
  returns numeric as $func$
declare
  _d_id           numeric;
  _c_id           numeric;
  _p_id           numeric;
  _quarter        numeric;
  _latest_quarter numeric;
  _s_id           numeric;

  _department     varchar;
  _number         varchar;
  _title          varchar;

  _professor1     varchar[];
  _professor2     varchar[];
  _professor3     varchar[];

  _professors     varchar[][];
  _professor      varchar[];

  _count          numeric := 0;
  _new_course     boolean := false;

begin
  for
    _quarter,
    _department,
    _number,
    _title,
    _professor1,
    _professor2,
    _professor3
  in
  select
    (course ->> 'term')::int as _quarter,
    course ->> 'subject' as _department,
    course ->> 'catalog_nbr' as _number,
    course ->> 'class_descr' as _title,

    -- prof #1
    case
    when (course ->> 'instr_1') like '%, %' then
        array[
          split_part(course ->> 'instr_1', ', ', 1),
          split_part(course ->> 'instr_1', ', ', 2)
        ]
    when (course ->> 'instr_1') = '' then
        null
    end as _professor1,

    -- prof #2
    case
    when (course ->> 'instr_2') like '%, %' then
      array[
      split_part(course ->> 'instr_2', ', ', 1),
      split_part(course ->> 'instr_2', ', ', 2)
      ]
    when (course ->> 'instr_2') = '' then
      null
    end as _professor2,

    -- prof #3
    case
    when (course ->> 'instr_3') like '%, %' then
      array[
      split_part(course ->> 'instr_3', ', ', 1),
      split_part(course ->> 'instr_3', ', ', 2)
      ]
    when (course ->> 'instr_3') = '' then
      null
    end as _professor3

  from jsonb_array_elements(_json -> 'courses') course
  loop

    if _professor1 is null then continue; end if;

    -- get the department id (assume it exists)
    select departments.id into _d_id
    from departments
    where abbreviation = _department
    order by school_id limit 1;

    -- get the course id if it exists
    select id into _c_id
    from courses
    where department_id = _d_id and number = _number;

    -- if the course does not exist, create it
    if _c_id is null then
      insert into courses (department_id, number, title) values (_d_id, _number, _title)
      returning id into _c_id;

      _new_course = true;
    end if;

    -- get the section id if it exists
    select id into _s_id
    from sections
    where quarter_id = _quarter and course_id = _c_id;

    -- if the section does not exist, create it
    if _s_id is null then
      insert into sections (quarter_id, course_id) values (_quarter, _c_id)
      returning id into _s_id;
    end if;

    _professors = array[_professor1];
    if _professor2 is not null then _professors = array_cat(_professors, _professor2); end if;
    if _professor3 is not null then _professors = array_cat(_professors, _professor3); end if;

    foreach _professor slice 1 in array _professors
    loop

      if _professor[1] is null then continue; end if;

      -- get the professor id if it exists
      select id into _p_id
      from professors
      where last_name = _professor[2] and first_name = _professor[1];

      -- if the professor does not exist, create it
      if  _p_id is null then
        insert into professors (first_name, last_name, university_id)
        values (_professor[1], _professor[2], _university_id)
        returning id into _p_id;
      end if;

      -- check if the professer is listed under this section
      if not exists(select 1
                    from section_professor sp
                    where sp.section_id = _s_id and sp.professor_id = _p_id)
      then
        insert into section_professor (section_id, professor_id) values (_s_id, _p_id);
      end if;
    end loop;

    -- if the course existed, make sure the title is up to date
    if not _new_course then
      -- get the latest quarter which the course was offered in
      select q.id into _latest_quarter
      from quarters q
        join sections s on q.id = s.quarter_id
        join courses c on s.course_id = c.id
      where c.id = _c_id and q.university_id = _university_id
      order by lower(period) desc
      limit 1;

      -- if this course info is for the latest quarter, update the title
      if _quarter = _latest_quarter then
        update courses
        set title = _title
        where id = _c_id;
      end if;

    end if;

    _count = _count + 1;
  end loop;

  return _count;
end;
$func$ language plpgsql;"""))


def downgrade():
    pass
