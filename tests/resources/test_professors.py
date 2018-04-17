import json
from urllib.parse import urlencode

from tests.fixtures.factories import (
    SectionFactory, ProfessorFactory, QuarterFactory, CourseFactory, StudentFactory, EvaluationFactory, VoteFactory
)
from scuevals_api.models import db
from tests import TestCase, assert_valid_schema


class ProfessorsTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.quarter1 = QuarterFactory()
        self.quarter2 = QuarterFactory()
        self.course = CourseFactory()
        professor = ProfessorFactory()
        professor2 = ProfessorFactory()
        SectionFactory(course=self.course, quarter=self.quarter1, professors=[professor])
        SectionFactory(course=self.course, quarter=self.quarter2, professors=[professor2])

        db.session.flush()

    def test_get(self):
        rv = self.client.get('/professors', headers=self.head_auth)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_filter(self):
        query = urlencode({'quarter_id': self.quarter1.id, 'course_id': self.course.id})
        rv = self.client.get('/professors', headers=self.head_auth, query_string=query)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))


class ProfessorsTopTestCase(TestCase):
    def setUp(self):
        p1 = ProfessorFactory()
        p2 = ProfessorFactory()
        p3 = ProfessorFactory()
        p4 = ProfessorFactory()

        self.s1 = SectionFactory(professors=[p1])
        self.s2 = SectionFactory(professors=[p2])
        s3 = SectionFactory(professors=[p3])
        SectionFactory(professors=[p4])

        EvaluationFactory(section=self.s1, professor=p1)
        EvaluationFactory(section=self.s2, professor=p2)
        EvaluationFactory(section=s3, professor=p3)

    def test_get(self):
        rv = self.client.get('/professors/top', headers=self.head_auth, query_string=urlencode({'count': 2}))

        self.assertEqual(200, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_department_ids(self):
        rv = self.client.get('/professors/top', headers=self.head_auth,
                             query_string=urlencode({
                                 'department_id': [self.s1.course.department_id, self.s2.course.department_id]
                             }, True))

        self.assertEqual(200, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual(2, len(data))


class ProfessorTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.course = CourseFactory()
        self.prof = ProfessorFactory()
        prof2 = ProfessorFactory()
        prof3 = ProfessorFactory()
        student = StudentFactory()
        section = SectionFactory(course=self.course, professors=[self.prof, prof2, prof3])

        # prof has taught this course twice
        SectionFactory(course=self.course, professors=[self.prof])

        SectionFactory(professors=[self.prof])
        EvaluationFactory(student=self.student, professor=self.prof, section=section)
        evaluation = EvaluationFactory(student=student, professor=self.prof, section=section)
        VoteFactory(student=self.student, evaluation=evaluation)

        db.session.flush()

    def test_get(self):
        rv = self.client.get('/professors/{}'.format(self.prof.id), headers=self.head_auth)
        self.assertEqual(200, rv.status_code)

        assert_valid_schema(rv.data, 'professor_with_evals.json')

        data = json.loads(rv.data)
        self.assertEqual(2, len(data['evaluations']))

    def test_get_embed_courses(self):
        rv = self.client.get('/professors/{}'.format(self.prof.id),
                             headers=self.head_auth,
                             query_string=urlencode({'embed': 'courses'}))

        self.assertEqual(200, rv.status_code)

        assert_valid_schema(rv.data, 'professor_with_evals_courses.json')

        data = json.loads(rv.data)
        self.assertEqual(2, len(data['evaluations']))
        self.assertEqual(2, len(data['courses']))

    def test_get_non_existing(self):
        rv = self.client.get('/professors/0', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])
