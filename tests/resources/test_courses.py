import json
from urllib.parse import urlencode

from tests.fixtures.factories import (
    StudentFactory, ProfessorFactory, SectionFactory, CourseFactory, EvaluationFactory, VoteFactory,
    QuarterFactory, DepartmentFactory
)
from scuevals_api.models import db, Vote
from tests import TestCase, use_data, assert_valid_schema, no_logging


class CoursesTestCase(TestCase):

    def test_get(self):
        CourseFactory()
        CourseFactory()

        rv = self.client.get('/courses', headers=self.head_auth)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_quarter_id(self):
        quarter = QuarterFactory()
        quarter2 = QuarterFactory()
        course = CourseFactory()
        course2 = CourseFactory()
        SectionFactory(quarter=quarter, course=course)
        SectionFactory(quarter=quarter2, course=course2)

        rv = self.client.get('/courses',
                             headers=self.head_auth,
                             query_string=urlencode({'quarter_id': quarter.id}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    def test_get_professor_id(self):
        course = CourseFactory()
        course2 = CourseFactory()
        prof = ProfessorFactory()
        SectionFactory(course=course)
        SectionFactory(course=course2, professors=[prof])

        rv = self.client.get('/courses',
                             headers=self.head_auth,
                             query_string=urlencode({'professor_id': prof.id}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    def test_get_quarter_id_professor_id(self):
        quarter = QuarterFactory()
        quarter2 = QuarterFactory()
        course = CourseFactory()
        course2 = CourseFactory()
        prof = ProfessorFactory()
        SectionFactory(quarter=quarter, course=course)
        SectionFactory(quarter=quarter2, course=course2, professors=[prof])

        rv = self.client.get('/courses', headers=self.head_auth, query_string=urlencode({
            'professor_id': prof.id, 'quarter_id': quarter2.id
        }))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    @use_data('courses.yaml')
    def test_post(self, data):
        QuarterFactory(id=3900)
        DepartmentFactory(abbreviation='ANTH')
        DepartmentFactory(abbreviation='COMM')
        db.session.flush()

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

        with no_logging():
            rv = self.client.post('/courses', headers=headers, data=data['courses_missing_department'])

        self.assertEqual(422, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual('missing department ACTG', resp['message'])

    @use_data('courses.yaml')
    def test_post_invalid_quarter(self, data):
        DepartmentFactory(abbreviation='ANTH')
        db.session.flush()

        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        with no_logging():
            rv = self.client.post('/courses', headers=headers, data=data['courses_invalid_quarter'])

        self.assertEqual(422, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('semantic errors', data['message'])


class CoursesTopTestCase(TestCase):
    def setUp(self):
        self.s1 = SectionFactory()
        self.s2 = SectionFactory()
        s3 = SectionFactory()
        SectionFactory()

        EvaluationFactory(section=self.s1)
        EvaluationFactory(section=self.s1)
        EvaluationFactory(section=self.s2)
        EvaluationFactory(section=s3)

    def test_get(self):
        rv = self.client.get('/courses/top', headers=self.head_auth, query_string=urlencode({'count': 2}))

        self.assertEqual(200, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_department_ids(self):
        rv = self.client.get('/courses/top', headers=self.head_auth,
                             query_string=urlencode({
                                 'department_id': [self.s1.course.department_id, self.s2.course.department_id]
                             }, True))

        self.assertEqual(200, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual(2, len(data))


class CourseTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.course = CourseFactory()
        prof = ProfessorFactory()
        prof2 = ProfessorFactory()
        prof3 = ProfessorFactory()
        student = StudentFactory()

        section = SectionFactory(course=self.course, professors=[prof, prof2, prof3])

        # prof2 has taught this course multiple quarters
        SectionFactory(course=self.course, professors=[prof2])

        EvaluationFactory(student=self.student, professor=prof, section=section)
        evaluation = EvaluationFactory(student=student, professor=prof, section=section)
        VoteFactory(student=self.student, evaluation=evaluation, value=Vote.UPVOTE)

        db.session.flush()

    def test_get(self):
        rv = self.client.get('/courses/{}'.format(self.course.id), headers=self.head_auth)
        self.assertEqual(200, rv.status_code)

        assert_valid_schema(rv.data, 'course_with_evals.json')

        data = json.loads(rv.data)
        self.assertEqual(2, len(data['evaluations']))

    def test_get_embed_professors(self):
        rv = self.client.get('/courses/{}'.format(self.course.id),
                             headers=self.head_auth,
                             query_string=urlencode({'embed': 'professors'}))

        self.assertEqual(200, rv.status_code)

        assert_valid_schema(rv.data, 'course_with_evals_professors.json')

        data = json.loads(rv.data)
        self.assertEqual(2, len(data['evaluations']))
        self.assertEqual(3, len(data['professors']))

    def test_get_non_existing(self):
        rv = self.client.get('/courses/0', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])
