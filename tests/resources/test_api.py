import json

from tests import TestCase


class APIStatusTestCase(TestCase):

    def test_get(self):
        rv = self.client.get('/')

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertIn('status', data)
        self.assertEqual('ok', data['status'])
