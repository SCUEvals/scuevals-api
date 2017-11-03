import json
import time

from jose import jwt
from json import JSONDecodeError
from tests import TestCase, use_data, vcr
from scuevals_api.models import db, APIKey


class AuthTestCase(TestCase):

    def setUp(self):
        super(AuthTestCase, self).setUp()

        with self.appx.app_context():
            db.session.add(APIKey(key='API_KEY', university_id=1))
            db.session.commit()

    @use_data('auth.yaml')
    @vcr.use_cassette
    def test_auth(self, data):
        # make sure the new token will have a new expiration time
        time.sleep(1)

        old_jwt = jwt.get_unverified_claims(self.jwt)

        rv = self.app.post('/auth', headers={'Content-Type': 'application/json'},
                           data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(rv.status_code, 200)

        try:
            resp = json.loads(rv.data)
        except JSONDecodeError:
            self.fail('invalid response')

        self.assertIn('jwt', resp)

        new_data = jwt.get_unverified_claims(resp['jwt'])

        self.assertGreater(new_data['exp'], old_jwt['exp'])

    def test_validation(self):
        # make sure the new token will have a new expiration time
        time.sleep(1)

        data = jwt.get_unverified_claims(self.jwt)

        rv = self.app.get('/auth/validate', headers={'Authorization': 'Bearer ' + self.jwt})

        self.assertEqual(rv.status_code, 200)

        try:
            resp = json.loads(rv.data)
        except JSONDecodeError:
            self.fail('invalid response')

        self.assertIn('jwt', resp)

        new_data = jwt.get_unverified_claims(resp['jwt'])

        self.assertGreater(new_data['exp'], data['exp'])

    def test_auth_api(self):
        rv = self.app.post('/auth/api', headers={'Content-Type': 'application/json'},
                           data=json.dumps({'api_key': 'API_KEY'}))

        self.assertEqual(rv.status_code, 200)

        try:
            resp = json.loads(rv.data)
        except JSONDecodeError:
            self.fail('invalid response')

        self.assertIn('jwt', resp)

        claims = jwt.get_unverified_claims(resp['jwt'])
        self.assertIn('roles', claims['sub'])
        self.assertEqual([20], claims['sub']['roles'])

    def test_api_unauthorized(self):
        rv = self.app.post('/auth/api', headers={'Content-Type': 'application/json'},
                           data=json.dumps({'api_key': 'INVALID_KEY'}))

        self.assertEqual(rv.status_code, 401)

    def test_invalid_jwt(self):
        rv = self.app.get('/auth/validate', headers={'Authorization': 'Bearer foobar'})
        self.assertEqual(rv.status_code, 422)
