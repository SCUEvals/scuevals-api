import json

from tests import TestCase, use_data, no_logging
from tests.fixtures.factories import DepartmentFactory


class DepartmentsTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

    def test_get(self):
        DepartmentFactory(abbreviation='MATH')
        DepartmentFactory(abbreviation='ENGL')

        rv = self.client.get('/departments', headers=self.head_auth)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)

        # the two departments above + the one in the original setup
        self.assertEqual(len(data), 3)

    @use_data('departments.yaml')
    def test_post(self, data):
        rv = self.client.post('/departments', headers=self.headers, data=data['departments'])
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual(74, resp['updated_count'])

    @use_data('departments.yaml')
    def test_post_invalid_school(self, data):
        with no_logging():
            rv = self.client.post('/departments', headers=self.headers, data=data['departments_invalid'])

        self.assertEqual(422, rv.status_code)
