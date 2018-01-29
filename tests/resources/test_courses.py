import json
from urllib.parse import urlencode

from flask_jwt_extended import create_access_token

from scuevals_api.models import (
    db, Quarter, Department, Course, Section, Evaluation,
    Professor, Student, University, Vote
)
from tests import TestCase, use_data


class CoursesTestCase(TestCase):
    def setUp(self):
        super().setUp()

        db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                               period='[2017-01-01, 2017-02-01]', university_id=1))
        db.session.add(Quarter(id=2, year=2017, name='Spring', current=False,
                               period='[2017-03-01, 2017-04-01]', university_id=1))
        db.session.add(Quarter(id=3900, year=2017, name='Fall', current=False,
                               period='[2017-05-01, 2017-06-01]', university_id=1))
        db.session.add(Department(id=1, abbreviation='ANTH', name='Anthropology', school_id=1))
        db.session.add(Department(id=2, abbreviation='COMM', name='Communications', school_id=1))
        db.session.add(Course(id=1000, title='Math Course', number='1', department_id=1))
        db.session.add(Course(id=1001, title='Arts Course', number='2', department_id=1))
        db.session.add(Section(quarter_id=1, course_id=1000))

        section = Section(quarter_id=2, course_id=1001)
        db.session.add(section)

        section.professors.append(Professor(id=0, first_name='Peter', university_id=1))

        db.session.flush()

    def test_get(self):
        rv = self.client.get('/courses', headers=self.head_auth)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_quarter_id(self):
        rv = self.client.get('/courses', headers=self.head_auth, query_string=urlencode({'quarter_id': 1}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    def test_get_professor_id(self):
        rv = self.client.get('/courses', headers=self.head_auth, query_string=urlencode({'professor_id': 0}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    def test_get_quarter_id_professor_id(self):
        rv = self.client.get('/courses', headers=self.head_auth, query_string=urlencode({
            'professor_id': 0, 'quarter_id': 2
        }))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

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
        super().setUp()

        db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                               period='[2017-01-01, 2017-02-01]', university_id=1))
        db.session.add(Department(id=1, abbreviation='MATH', name='Mathematics', school_id=1))
        db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
        db.session.add(Section(id=1, quarter_id=1, course_id=1))
        db.session.add(Professor(id=1, first_name='Ben', last_name='Stiller', university_id=1))
        db.session.add(Student(id=1, email='sdoe@scu.edu', first_name='Sandra', last_name='Doe', university_id=1))
        db.session.add(Evaluation(
            id=1, student_id=0, professor_id=1, section_id=1, version=1, data={'q1': 'a1'},
            display_grad_year=True, display_majors=False
        ))
        db.session.add(Evaluation(
            id=2, student_id=1, professor_id=1, section_id=1, version=1, data={'q1': 'a1'},
            display_grad_year=True, display_majors=False
        ))
        db.session.add(Vote(student_id=0, evaluation_id=2, value=Vote.UPVOTE))

    def test_get(self):
        rv = self.client.get('/courses/1', headers=self.head_auth)
        self.assertEqual(200, rv.status_code)

        expected = {
            'id': 1,
            'number': '1',
            'title': 'Math Course',
            'department_id': 1,
            'evaluations': [
                {
                    'id': 1,
                    'quarter_id': 1,
                    'version': 1,
                    'votes_score': 0,
                    'user_vote': None,
                    'data': {'q1': 'a1'},
                    'professor': {
                        'id': 1,
                        'first_name': 'Ben',
                        'last_name': 'Stiller'
                    },
                    'author': {
                        'self': True,
                        'graduation_year': 2020,
                        'majors': None
                    }
                },
                {
                    'id': 2,
                    'quarter_id': 1,
                    'version': 1,
                    'votes_score': 1,
                    'user_vote': 'u',
                    'data': {'q1': 'a1'},
                    'professor': {
                        'id': 1,
                        'first_name': 'Ben',
                        'last_name': 'Stiller'
                    },
                    'author': {
                        'self': False,
                        'majors': None,
                        'graduation_year': None
                    }
                }
            ]
        }

        self.assertEqual(expected, json.loads(rv.data))

    def test_get_wrong_university(self):
        db.session.add(University(id=2, abbreviation='UCB', name='UC Berkeley'))
        student = Student.query.get(0)
        student.university_id = 2

        student = Student.query.get(0)
        ident = student.to_dict()

        jwt = create_access_token(identity=ident)

        rv = self.client.get('/courses/1', headers={'Authorization': 'Bearer ' + jwt})
        self.assertEqual(401, rv.status_code)

    def test_get_non_existing(self):
        rv = self.client.get('/courses/0', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])
