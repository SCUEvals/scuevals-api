import json

from flask_jwt_extended import create_access_token

from scuevals_api.models import db, Role
from tests.fixtures.factories import StudentFactory
from tests import TestCase, no_logging


class MajorsTestCase(TestCase):
    def test_get_as_student(self):
        rv = self.client.get('/majors', headers=self.head_auth)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual(1, len(data))

    def test_majors_as_incomplete(self):
        incomplete = StudentFactory(roles=[Role.query.get(Role.Incomplete)])
        db.session.flush()
        jwt = create_access_token(identity=incomplete.to_dict())
        head_auth = {'Authorization': 'Bearer ' + jwt}

        rv = self.client.get('/majors', headers=head_auth)

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

        with no_logging():
            rv = self.client.post('/majors', headers=headers, data=json.dumps(data))

        self.assertEqual(422, rv.status_code)
