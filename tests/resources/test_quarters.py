import json
from urllib.parse import urlencode

from scuevals_api.models import db, Quarter, Department, Course, Section, Professor
from tests import TestCase, assert_valid_schema


class QuartersTestCase(TestCase):
    def setUp(self):
        super(QuartersTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Quarter(id=2, year=2017, name='Spring', current=False,
                                   period='[2017-03-01, 2017-04-01]', university_id=1))
            db.session.add(Department(abbreviation='ANTH', name='Anthropology', school_id=1))
            db.session.add(Department(abbreviation='COMM', name='Communications', school_id=1))
            db.session.add(Course(id=1000, title='Math Course', number='1', department_id=1))
            db.session.add(Course(id=1001, title='Arts Course', number='2', department_id=1))
            db.session.add(Section(quarter_id=1, course_id=1000))

            section = Section(quarter_id=2, course_id=1001)
            db.session.add(section)

            section.professors.append(Professor(id=0, first_name='Peter', university_id=1))
            db.session.commit()

    def test_get(self):
        rv = self.client.get('/quarters', headers=self.head_auth)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))
        assert_valid_schema(rv.data, 'quarters.json')

    def test_get_course_id(self):
        rv = self.client.get('/quarters', headers=self.head_auth, query_string=urlencode({'course_id': 1000}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))
        assert_valid_schema(rv.data, 'quarters.json')

    def test_get_professor_id(self):
        rv = self.client.get('/quarters', headers=self.head_auth, query_string=urlencode({'professor_id': 0}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))
        assert_valid_schema(rv.data, 'quarters.json')
