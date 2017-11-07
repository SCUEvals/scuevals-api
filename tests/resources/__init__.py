import json
from flask_jwt_extended import create_access_token

from scuevals_api.models import Student
from tests import TestCase


class ResourceTestCase(TestCase):
    def setUp(self):
        super(ResourceTestCase, self).setUp()

        with self.app.app_context():
            student = Student(
                id=0,
                email='jdoe@scu.edu',
                first_name='John',
                last_name='Doe',
                university_id=1
            )
            ident = student.to_dict()
            self.jwt = create_access_token(identity=ident)

    def test_no_roles(self):
        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.client.get('/quarters', headers=headers)
        self.assertEqual(rv.status_code, 401)

    def test_wrong_mimetype(self):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
        }

        data = {'majors': ['Major1']}

        rv = self.client.post('/majors', headers=headers, data=json.dumps(data))
        self.assertEqual(415, rv.status_code)

    def test_wrong_args(self):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        data = {'invalid': 'data'}

        rv = self.client.post('/majors', headers=headers, data=json.dumps(data))
        self.assertEqual(422, rv.status_code)