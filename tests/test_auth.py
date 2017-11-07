import json
import time
from unittest import mock

from flask_jwt_extended import create_access_token
from jose import jwt
from json import JSONDecodeError
from tests import TestCase, use_data, vcr
from scuevals_api.models import db, APIKey, Student, Role


class AuthTestCase(TestCase):
    def setUp(self):
        super(AuthTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(APIKey(key='API_KEY', university_id=1))
            db.session.commit()

    @use_data('auth.yaml')
    @vcr.use_cassette
    def test_auth(self, data):
        # make sure the new token will have a new expiration time
        time.sleep(1)

        old_jwt = jwt.get_unverified_claims(self.jwt)

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
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

        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer ' + self.jwt})

        self.assertEqual(rv.status_code, 200)

        try:
            resp = json.loads(rv.data)
        except JSONDecodeError:
            self.fail('invalid response')

        self.assertIn('jwt', resp)

        new_data = jwt.get_unverified_claims(resp['jwt'])

        self.assertGreater(new_data['exp'], data['exp'])

    def test_auth_api(self):
        rv = self.client.post('/auth/api', headers={'Content-Type': 'application/json'},
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
        rv = self.client.post('/auth/api', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'api_key': 'INVALID_KEY'}))

        self.assertEqual(rv.status_code, 401)

    def test_invalid_jwt(self):
        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer foobar'})
        self.assertEqual(rv.status_code, 422)

    def test_invalid_jwt_claims(self):
        invalid_ident = {'university_id': 1}

        with self.app.app_context():
            self.jwt = create_access_token(identity=invalid_ident)

        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(400, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual('User claims verification failed', data['msg'])

    @use_data('auth.yaml')
    @vcr.use_cassette('test_auth')
    def test_id_token_expired(self, data):
        self.app.debug = False
        self.client = self.app.test_client()

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(401, rv.status_code)

    def test_id_token_invalid_format(self):
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': 'foo'}))
        self.assertEqual(422, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('invalid id_token format:', data['message'])

    @use_data('auth.yaml')
    @vcr.use_cassette('test_auth')
    def test_id_token_invalid(self, data):
        self.app.debug = False
        self.client = self.app.test_client()

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token_invalid']}))
        self.assertEqual(422, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('invalid id_token:', data['message'])

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'foo.edu'})
    @vcr.use_cassette('test_auth')
    def test_id_token_invalid_hd(self, data, decode_func):
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token_invalid']}))
        self.assertEqual(422, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('invalid id_token', data['message'])

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'scu.edu', 'email': 'jdoe@scu.edu', 'picture': 'foo.jpg'})
    @vcr.use_cassette('test_auth')
    def test_id_token_existing_user(self, data, decode_func):
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(200, rv.status_code)

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'scu.edu', 'email': 'jdoe@scu.edu', 'picture': 'foo.jpg'})
    @vcr.use_cassette('test_auth')
    def test_id_token_existing_user_incomplete(self, data, decode_func):
        with self.app.app_context():
            student = Student.query.get(0)
            student.roles_list = [Role.Incomplete]
            db.session.commit()

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(200, rv.status_code)

    @use_data('auth.yaml')
    @vcr.use_cassette
    def test_google_openid_error(self, data):
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(500, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('failed to get Google openid config', data['message'])

    @use_data('auth.yaml')
    @vcr.use_cassette
    def test_google_jwks_error(self, data):
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(500, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('failed to get certificates from Google', data['message'])
