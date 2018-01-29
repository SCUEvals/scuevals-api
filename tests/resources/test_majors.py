import json

from tests import TestCase


class MajorsTestCase(TestCase):
    def test_majors(self):
        rv = self.client.get('/majors', headers=self.head_auth)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    def test_post(self):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        data = {'majors': ['Major1', 'Major2', 'Major3']}

        rv = self.client.post('/majors', headers=headers, data=json.dumps(data))
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual('success', resp['result'])

    def test_post_duplicate_majors(self):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        data = {'majors': ['Major1', 'Major1']}

        rv = self.client.post('/majors', headers=headers, data=json.dumps(data))
        self.assertEqual(422, rv.status_code)
