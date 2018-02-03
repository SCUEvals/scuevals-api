import json
from urllib.parse import urlencode

from tests.fixtures.factories import (
    StudentFactory, ProfessorFactory, SectionFactory, CourseFactory, EvaluationFactory, VoteFactory
)
from scuevals_api.models import db, Quarter, Department, Course, Section, Professor, Vote
from tests import TestCase, use_data, assert_valid_schema


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

        self.course = CourseFactory()
        prof = ProfessorFactory()
        prof2 = ProfessorFactory()
        prof3 = ProfessorFactory()
        student = StudentFactory()
        section = SectionFactory(course=self.course, professors=[prof, prof2, prof3])
        EvaluationFactory(student=self.student, professor=prof, section=section)
        evaluation = EvaluationFactory(student=student, professor=prof, section=section)
        VoteFactory(student=self.student, evaluation=evaluation, value=Vote.UPVOTE)

        db.session.flush()

    def test_get(self):
        rv = self.client.get('/courses/{}'.format(self.course.id), headers=self.head_auth)
        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data['evaluations']))

        assert_valid_schema(rv.data, 'course_with_evals.json')

    def test_get_embed_professors(self):
        rv = self.client.get('/courses/{}'.format(self.course.id),
                             headers=self.head_auth,
                             query_string=urlencode({'embed': 'professors'}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data['evaluations']))
        self.assertEqual(3, len(data['professors']))

        assert_valid_schema(rv.data, 'course_with_evals_professors.json')

    def test_get_non_existing(self):
        rv = self.client.get('/courses/0', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])
