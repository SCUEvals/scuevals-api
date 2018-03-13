import json

from flask_jwt_extended import create_access_token

from scuevals_api.models import db
from tests import TestCase
from tests.fixtures.factories import StudentFactory


class JWTTestCase(TestCase):
    def test_user_loader(self):
        # create a jwt for a non-existing user
        student = StudentFactory()
        db.session.flush()
        info = student.to_dict()
        info['id'] += 1

        token = create_access_token(identity=info)

        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer ' + token})

        self.assertEqual(500, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual('unable to load user', data['message'])
