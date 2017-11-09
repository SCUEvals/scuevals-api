import json
from urllib.parse import urlencode

from flask_jwt_extended import create_access_token

from scuevals_api.models import db, Quarter, Department, Course, Section, Evaluation, Professor, Student, University
from tests import TestCase, use_data


class CoursesTestCase(TestCase):
    def setUp(self):
        super(CoursesTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Quarter(id=2, year=2017, name='Spring', current=False,
                                   period='[2017-03-01, 2017-04-01]', university_id=1))
            db.session.add(Quarter(id=3900, year=2017, name='Fall', current=False,
                                   period='[2017-05-01, 2017-06-01]', university_id=1))
            db.session.add(Department(abbreviation='ANTH', name='Anthropology', school_id=1))
            db.session.add(Department(abbreviation='COMM', name='Communications', school_id=1))
            db.session.add(Course(id=1000, title='Math Course', number='1', department_id=1))
            db.session.add(Course(id=1001, title='Arts Course', number='2', department_id=1))
            db.session.add(Section(quarter_id=1, course_id=1000))
            db.session.add(Section(quarter_id=2, course_id=1001))
            db.session.commit()

    def test_get(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
        }

        rv = self.client.get('/courses', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)

    def test_get_quarter_id(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
        }

        rv = self.client.get('/courses', headers=headers, query_string=urlencode({'quarter_id': 1}))

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 1)

    @use_data('courses.yaml')
    def test_post(self, data):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.post('/courses', headers=headers, data=data['courses'])
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual(21, resp['updated_count'])

    @use_data('courses.yaml')
    def test_post_missing_department(self, data):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.post('/courses', headers=headers, data=data['courses_missing_department'])
        self.assertEqual(422, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual('missing department ACTG', resp['message'])

    @use_data('courses.yaml')
    def test_post_invalid_quarter(self, data):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.post('/courses', headers=headers, data=data['courses_invalid_quarter'])
        self.assertEqual(422, rv.status_code)


class CourseTestCase(TestCase):
    def setUp(self):
        super(CourseTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Department(abbreviation='MATH', name='Mathematics', school_id=1))
            db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
            db.session.add(Section(id=1, quarter_id=1, course_id=1))
            db.session.add(Professor(id=1, first_name='Ben', last_name='Stiller', university_id=1))
            db.session.add(Evaluation(student_id=0, professor_id=1, section_id=1, version=1, data={'q1': 'a1'}))
            db.session.commit()

    def test_get(self):
        rv = self.client.get('/courses/1', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(200, rv.status_code)

        expected = {
            'id': 1,
            'department': {
                'id': 1,
                'abbreviation': 'MATH'
            },
            'name': '1',
            'title': 'Math Course',
            'evaluations': [
                {
                    'id': 1,
                    'quarter_id': 1,
                    'version': 1,
                    'data': {'q1': 'a1'},
                    'professor': {
                        'id': 1,
                        'first_name': 'Ben',
                        'last_name': 'Stiller'
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
