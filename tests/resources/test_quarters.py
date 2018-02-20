import json
from urllib.parse import urlencode

from tests import TestCase, assert_valid_schema
from tests.fixtures.factories import CourseFactory
from tests.fixtures.factories import QuarterFactory
from tests.fixtures.factories import SectionFactory
from tests.fixtures.factories import ProfessorFactory


class QuartersTestCase(TestCase):
    schema_get = 'quarters.json'

    def setUp(self):
        super().setUp()

        q1 = QuarterFactory()
        q2 = QuarterFactory()
        QuarterFactory(current=True)

        c1 = CourseFactory(id=1000)
        CourseFactory()

        s1 = SectionFactory(quarter=q1, course=c1)
        s2 = SectionFactory(quarter=q2, course=c1)

        ProfessorFactory(id=1000, sections=[s1])
        ProfessorFactory(sections=[s2])

    def test_get(self):
        rv = self.client.get('/quarters', headers=self.head_auth)

        self.assertEqual(200, rv.status_code)
        assert_valid_schema(rv.data, self.schema_get)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_course_id(self):
        rv = self.client.get('/quarters', headers=self.head_auth, query_string=urlencode({'course_id': 1000}))

        self.assertEqual(200, rv.status_code)
        assert_valid_schema(rv.data, self.schema_get)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    def test_get_professor_id(self):
        rv = self.client.get('/quarters', headers=self.head_auth, query_string=urlencode({'professor_id': 1000}))

        self.assertEqual(200, rv.status_code)
        assert_valid_schema(rv.data, self.schema_get)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    def test_get_course_id_professor_id(self):
        rv = self.client.get('/quarters',
                             headers=self.head_auth,
                             query_string=urlencode({'professor_id': 1000, 'course_id': 1000}))

        self.assertEqual(200, rv.status_code)
        assert_valid_schema(rv.data, self.schema_get)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))
