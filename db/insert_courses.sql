CREATE OR REPLACE FUNCTION insert_courses(_quarter NUMERIC, _json JSONB)
  RETURNS VOID AS $func$
DECLARE
  _d_id NUMERIC;
  _c_id NUMERIC;
  _department VARCHAR;
  _number VARCHAR;
BEGIN
  FOR _department, _number IN
    SELECT
      split_part(course ->> 'value', ' ', 1) AS _department,
      split_part(course ->> 'value', ' ', 2) AS _number
    FROM jsonb_array_elements(_json -> 'results') course
  LOOP
    SELECT department.id INTO _d_id FROM department WHERE abbreviation = _department;
    SELECT id INTO _c_id FROM course WHERE department_id = _d_id AND number = _number;

    IF _c_id IS NULL THEN
      INSERT INTO course (department_id, number) VALUES (_d_id, _number) RETURNING id INTO _c_id;
    END IF;

    IF NOT EXISTS(SELECT 1 FROM quarter_course WHERE course_id = _c_id AND quarter_id = _quarter) THEN
      INSERT INTO quarter_course (quarter_id, course_id) VALUES (_quarter, _c_id);
    END IF;

  END LOOP;
END;
$func$ LANGUAGE plpgsql;