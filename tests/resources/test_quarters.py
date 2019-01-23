import json
from urllib.parse import urlencode
from datetime import date

from freezegun import freeze_time
from psycopg2.extras import DateRange

from tests import TestCase
from tests.fixtures.factories import CourseFactory
from tests.fixtures.factories import QuarterFactory
from tests.fixtures.factories import SectionFactory
from tests.fixtures.factories import ProfessorFactory


class QuartersTestCase(TestCase):
    schema_get = 'quarters.json'

    @classmethod
    @freeze_time('2018-03-05')
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

        q1 = QuarterFactory(period=DateRange(date(2018, 1, 1), date(2018, 2, 1)))
        q2 = QuarterFactory(period=DateRange(date(2018, 2, 1), date(2018, 3, 1)))
        QuarterFactory(period=DateRange(date(2018, 3, 1), date(2018, 4, 1)))

        c1 = CourseFactory(id=1000)
        CourseFactory()

        s1 = SectionFactory(quarter=q1, course=c1)
        s2 = SectionFactory(quarter=q2, course=c1)

        ProfessorFactory(id=1000, sections=[s1])
        ProfessorFactory(sections=[s2])

    @freeze_time('2018-03-05')
    def test_get(self):
        rv = self.client.get('/quarters', headers=self.head_auth)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    @freeze_time('2018-03-05')
    def test_get_course_id(self):
        rv = self.client.get('/quarters', headers=self.head_auth, query_string=urlencode({'course_id': 1000}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(2, len(data))

    @freeze_time('2018-03-05')
    def test_get_professor_id(self):
        rv = self.client.get('/quarters', headers=self.head_auth, query_string=urlencode({'professor_id': 1000}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    @freeze_time('2018-03-05')
    def test_get_course_id_professor_id(self):
        rv = self.client.get('/quarters',
                             headers=self.head_auth,
                             query_string=urlencode({'professor_id': 1000, 'course_id': 1000}))

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))
