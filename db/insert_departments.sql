CREATE OR REPLACE FUNCTION insert_departments(_json JSONB)
  RETURNS VOID AS $func$
DECLARE
  _s_id   NUMERIC;
  _d_id   NUMERIC;
  _abbr   VARCHAR;
  _name   VARCHAR;
  _school VARCHAR;
BEGIN
  FOR _abbr, _name, _school IN
  SELECT
    department ->> 'value' AS _abbr,
    (regexp_matches(department ->> 'label', '.+(?=\()'))[1] AS _name,
    department ->> 'school' AS _school
  FROM jsonb_array_elements(_json -> 'results') department
  LOOP
    SELECT school.id INTO _s_id FROM school WHERE abbreviation = _school;
    SELECT id INTO _d_id FROM department WHERE school_id = _s_id AND abbreviation = _abbr;

    IF _d_id IS NULL THEN
      INSERT INTO department (abbreviation, name, school_id) VALUES (_abbr, _name, _s_id);
    END IF;

  END LOOP;
END;
$func$ LANGUAGE plpgsql;