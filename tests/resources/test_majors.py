import json

from scuevals_api.models import db, Major
from tests import TestCase


class MajorsTestCase(TestCase):
    def test_majors(self):
        with self.app.app_context():
            db.session.add(Major(id=1, university_id=1, name='Major1'))
            db.session.add(Major(id=2, university_id=1, name='Major2'))
            db.session.commit()

        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.client.get('/majors', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)

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