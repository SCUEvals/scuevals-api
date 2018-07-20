import json

from flask_jwt_extended import create_access_token

from scuevals_api.models import db
from tests import TestCase
from tests.fixtures.factories import StudentFactory


class AuthRequiredTestCase(TestCase):
    def test_incorrect_permissions(self):
        student = StudentFactory(permissions=[])
        db.session.flush()

        token = create_access_token(identity=student.to_dict())

        rv = self.client.get('/quarters', headers={'Authorization': 'Bearer ' + token})

        self.assertEqual(401, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('could not verify that you are authorized to access the URL requested', data['message'])

    def test_missing_authorization_header(self):
        rv = self.client.get('/quarters', headers={})

        self.assertEqual(401, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('authorization error', data['message'])
