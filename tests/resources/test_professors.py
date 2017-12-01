import json
from urllib.parse import urlencode

from scuevals_api.models import db, Quarter, Department, Course, Section, Evaluation, Professor
from tests import TestCase


class ProfessorsTestCase(TestCase):
    def setUp(self):
        super().setUp()

        with self.app.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Department(abbreviation='GEN', name='General', school_id=1))
            db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
            db.session.add(Professor(id=0, first_name='Mary', last_name='Doe', university_id=1))

            professor = Professor(id=1, first_name='Robert', last_name='Doe', university_id=1)
            section = Section(quarter_id=1, course_id=1)
            section.professors.append(professor)
            db.session.add(professor)
            db.session.add(section)
            db.session.commit()

    def test_get(self):
        rv = self.client.get('/professors', headers=self.head_auth)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_filter(self):
        query = urlencode({'quarter_id': 1, 'course_id': 1})
        rv = self.client.get('/professors', headers=self.head_auth, query_string=query)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))


class ProfessorTestCase(TestCase):
    def setUp(self):
        super(ProfessorTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Department(abbreviation='MATH', name='Mathematics', school_id=1))
            db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
            db.session.add(Section(id=1, quarter_id=1, course_id=1))
            db.session.add(Professor(id=1, first_name='Mary', last_name='Doe', university_id=1))
            db.session.add(Evaluation(student_id=0, professor_id=1, section_id=1, version=1, data={'q1': 'a1'}))
            db.session.commit()

    def test_get(self):
        rv = self.client.get('/professors/1', headers=self.head_auth)
        self.assertEqual(200, rv.status_code)

        expected = {
            'id': 1,
            'first_name': 'Mary',
            'last_name': 'Doe',
            'evaluations': [
                {
                    'id': 1,
                    'quarter_id': 1,
                    'version': 1,
                    'data': {
                        'q1': 'a1'
                    },
                    'votes_score': 0,
                    'course': {
                        'id': 1,
                        'name': '1',
                        'title': 'Math Course',
                        'department': {
                            'id': 1,
                            'abbreviation': 'MATH'
                        }
                    }
                }
            ]
        }

        self.assertEqual(expected, json.loads(rv.data))

    def test_get_non_existing(self):
        rv = self.client.get('/professors/0', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])
