import json
from urllib.parse import urlencode

from tests import TestCase
from tests.fixtures.factories import ProfessorFactory, CourseFactory


class SearchTestCase(TestCase):
    def setUp(self):
        super().setUp()

        ProfessorFactory(first_name='Mathias')
        CourseFactory(title='Math Stuff')

    def test_search(self):
        rv = self.client.get('/search', headers=self.head_auth, query_string=urlencode({'q': 'mat'}))
        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertIn('courses', data)
        self.assertIn('professors', data)
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(len(data['professors']), 1)
