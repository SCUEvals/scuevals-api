import json
import time
import os
from unittest import mock
from datetime import datetime, timedelta

from flask_jwt_extended import create_access_token
from jose import jwt
from json import JSONDecodeError

from tests.fixtures.factories import StudentFactory, OfficialUserTypeFactory, UserFactory, APIKeyFactory
from tests import TestCase, use_data, vcr
from scuevals_api.auth import cache
from scuevals_api.models import db, Permission


id_token_data = {
    'azp': '471296732031-0hqhs9au11ro6mt87cpv1gog7kbdruer.apps.googleusercontent.com',
    'aud': '471296732031-0hqhs9au11ro6mt87cpv1gog7kbdruer.apps.googleusercontent.com',
    'sub': '116863427253343930740',
    'hd': 'scu.edu',
    'email': 'astudent@scu.edu',
    'email_verified': True,
    'at_hash': '3DOWjzVDZxgIs7MNGr4dyw',
    'iss': 'accounts.google.com',
    'jti': 'b3d9967b4b4a3f95af24509dc93b1ce024cf111a',
    'iat': 1507796167,
    'exp': 1507799767,
    'name': 'A Student',
    'picture': 'https://lh3.googleusercontent.com/-ByXCWfs-xjA/AAAA/AAAAAAAAAAA/rabkS1ia12c/s96-c/photo.jpg',
    'given_name': 'A',
    'family_name': 'Student',
    'locale': 'en'
}


class AuthTestCase(TestCase):
    def setUp(self):
        super().setUp()
        os.environ['GOOGLE_CLIENT_ID'] = ''
        cache.clear()

    @use_data('auth.yaml')
    @vcr.use_cassette
    def test_auth(self, data):
        StudentFactory(email='fblomqvist@scu.edu')

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

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value=id_token_data)
    @vcr.use_cassette
    def test_student(self, data, decode_func):
        OfficialUserTypeFactory(email='astudent@scu.edu', type='student')
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))

        data = json.loads(rv.data)
        self.assertIn('status', data)
        self.assertEqual('new', data['status'])

        self.assertIn('jwt', data)
        identity = jwt.get_unverified_claims(data['jwt'])
        self.assertEqual([Permission.Incomplete], identity['sub']['permissions'])

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value=id_token_data)
    @vcr.use_cassette
    def test_non_student(self, data, decode_func):
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))

        data = json.loads(rv.data)
        self.assertIn('status', data)
        self.assertEqual('non-student', data['status'])

    @use_data('auth.yaml')
    @vcr.use_cassette('test_auth')
    def test_id_token_expired(self, data):
        self.app.debug = False
        self.client = self.app.test_client()

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(422, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual('invalid id_token: expired', data['message'])

    def test_id_token_invalid_format(self):
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': 'foo'}))
        self.assertEqual(422, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('invalid id_token: invalid format:', data['message'])

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
    def test_existing_user(self, data, decode_func):
        StudentFactory(email='jdoe@scu.edu')
        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(200, rv.status_code)

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'scu.edu', 'email': 'jdoe@scu.edu', 'picture': 'foo.jpg'})
    @vcr.use_cassette('test_auth')
    def test_existing_user_incomplete(self, data, decode_func):
        student = StudentFactory(email='jdoe@scu.edu')
        student.permissions_list = [Permission.Incomplete]

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(200, rv.status_code)

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'scu.edu', 'email': 'jdoe@scu.edu', 'picture': 'foo.jpg'})
    @vcr.use_cassette('test_auth')
    def test_existing_user_suspended(self, data, decode_func):
        StudentFactory(email='jdoe@scu.edu', suspended_until=(datetime.now() + timedelta(days=1)))

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(401, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual('suspended', data['status'])

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'scu.edu', 'email': 'jdoe@scu.edu', 'picture': 'foo.jpg'})
    @vcr.use_cassette('test_auth')
    def test_existing_user_suspension_expired(self, data, decode_func):
        student = StudentFactory(email='jdoe@scu.edu', suspended_until=(datetime.now() - timedelta(days=1)))

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual('ok', data['status'])
        self.assertEqual(None, student.suspended_until)

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'scu.edu', 'email': 'jdoe@scu.edu', 'picture': 'foo.jpg'})
    @vcr.use_cassette('test_auth')
    def test_existing_user_read_access_expired(self, data, decode_func):
        student = StudentFactory(email='jdoe@scu.edu', read_access_until=(datetime.now() - timedelta(days=1)))
        student.permissions_list = [
            Permission.ReadEvaluations, Permission.WriteEvaluations, Permission.VoteOnEvaluations
        ]

        rv = self.client.post('/auth', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual('ok', data['status'])

        self.assertEqual(None, student.read_access_until)
        self.assertNotIn(Permission.ReadEvaluations, student.permissions_list)
        self.assertNotIn(Permission.VoteOnEvaluations, student.permissions_list)

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


class AuthValidationTestCase(TestCase):
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

    def test_invalid_jwt(self):
        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer foobar'})
        self.assertEqual(422, rv.status_code)

    def test_invalid_jwt_claims(self):
        invalid_ident = {'university_id': 1}

        self.jwt = create_access_token(identity=invalid_ident)

        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(401, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual('invalid or expired user info', data['message'])

    def test_suspended(self):
        user = UserFactory()
        db.session.flush()
        user_jwt = create_access_token(identity=user.to_dict())
        user.suspended_until = datetime.now() + timedelta(days=1)

        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer ' + user_jwt})

        self.assertEqual(401, rv.status_code)

    def test_read_access_expired(self):
        student = StudentFactory(permissions=[Permission.query.get(Permission.ReadEvaluations)],
                                 read_access_until=(datetime.now() - timedelta(days=1)))
        db.session.flush()
        student_jwt = create_access_token(identity=student.to_dict())

        rv = self.client.get('/search?q=', headers={'Authorization': 'Bearer ' + student_jwt})

        self.assertEqual(401, rv.status_code)

        data = json.loads(rv.data)
        self.assertIn('message', data)
        self.assertIn('could not verify that you are authorized to access the URL requested', data['message'])

    def test_read_access_none(self):
        student = StudentFactory(permissions=[Permission.query.get(Permission.WriteEvaluations)],
                                 read_access_until=None)
        db.session.flush()
        student_jwt = create_access_token(identity=student.to_dict())

        rv = self.client.get('/auth/validate', headers={'Authorization': 'Bearer ' + student_jwt})

        self.assertEqual(200, rv.status_code)


class AuthRefreshTestCase(TestCase):
    def test_refresh(self):
        student = StudentFactory(email='jdoe@scu.edu', read_access_until=(datetime.now() - timedelta(days=1)))
        student.permissions_list = [
            Permission.ReadEvaluations, Permission.WriteEvaluations, Permission.VoteOnEvaluations
        ]

        db.session.flush()

        old_jwt = create_access_token(identity=student.to_dict())

        rv = self.client.get('/auth/refresh', headers={'Authorization': 'Bearer ' + old_jwt})
        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)

        new_identity = jwt.get_unverified_claims(data['jwt'])['sub']

        self.assertEqual(None, student.read_access_until)
        self.assertNotIn(Permission.ReadEvaluations, student.permissions_list)
        self.assertNotIn(Permission.VoteOnEvaluations, student.permissions_list)
        self.assertEqual([Permission.WriteEvaluations], new_identity['permissions'])

    @use_data('auth.yaml')
    @mock.patch('jose.jwt.decode', return_value={'hd': 'scu.edu', 'email': 'jdoe@scu.edu', 'picture': 'foo.jpg'})
    @vcr.use_cassette('test_auth')
    def test_existing_user_suspended(self, data, decode_func):
        student = StudentFactory(email='jdoe@scu.edu', suspended_until=(datetime.now() + timedelta(days=1)))

        db.session.flush()

        token = create_access_token(identity=student.to_dict())

        rv = self.client.get('/auth/refresh', headers={'Authorization': 'Bearer ' + token})

        self.assertEqual(401, rv.status_code)

        data = json.loads(rv.data)
        self.assertEqual('suspended', data['status'])


class AuthAPITestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.api_key = APIKeyFactory()
        cache.clear()

    def test_auth_api(self):
        rv = self.client.post('/auth/api', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'api_key': self.api_key.key}))

        self.assertEqual(rv.status_code, 200)

        resp = json.loads(rv.data)

        self.assertIn('jwt', resp)

        claims = jwt.get_unverified_claims(resp['jwt'])
        self.assertIn('permissions', claims['sub'])
        self.assertEqual(self.api_key.permissions_list, claims['sub']['permissions'])

    def test_api_unauthorized(self):
        rv = self.client.post('/auth/api', headers={'Content-Type': 'application/json'},
                              data=json.dumps({'api_key': 'INVALID_KEY'}))

        self.assertEqual(rv.status_code, 401)
