import json
from urllib.parse import urlencode

from flask_jwt_extended import create_access_token

from scuevals_api.models import db, Quarter, Department, Course, Section, Evaluation, Professor, Student, University
from tests import TestCase, use_data


class ProfessorsTestCase(TestCase):
    def setUp(self):
        super(ProfessorsTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Professor(id=0, first_name='Mary', last_name='Doe', university_id=1))
            db.session.add(Professor(id=1, first_name='Robert', last_name='Doe', university_id=1))
            db.session.commit()

    def test_get(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
        }

        rv = self.client.get('/professors', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)


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
        rv = self.client.get('/professors/1', headers={'Authorization': 'Bearer ' + self.jwt})
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

    def test_get_wrong_university(self):
        with self.app.app_context():
            db.session.add(University(id=2, abbreviation='UCB', name='UC Berkeley'))
            student = Student.query.get(0)
            student.university_id = 2

            ident = student.to_dict()
            db.session.commit()

            self.jwt = create_access_token(identity=ident)

        rv = self.client.get('/courses/1', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(401, rv.status_code)
