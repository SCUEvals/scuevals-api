import json
import time
from jose import jwt
from json import JSONDecodeError
from vcr import VCR
from helper import TestCase, use_data

vcr = VCR(
    cassette_library_dir='fixtures/cassettes',
    path_transformer=VCR.ensure_suffix('.yaml')
)


class AuthTestCase(TestCase):

    @use_data('test_auth.yaml')
    @vcr.use_cassette
    def test_auth(self, data):
        rv = self.app.post('/auth', headers={'Content-Type': 'application/json'},
                           data=json.dumps({'id_token': data['id_token']}))
        self.assertEqual(rv.status_code, 400)
        self.assertIn('Signature has expired', str(rv.data))

    def test_validation(self):
        # make sure the new token will have a new expiration time
        time.sleep(1)

        data = jwt.get_unverified_claims(self.jwt)

        rv = self.app.post('/auth/validate', headers={'Content-Type': 'application/json'},
                           data=json.dumps({'jwt': self.jwt}))

        self.assertEqual(rv.status_code, 200)

        try:
            resp = json.loads(rv.data)
        except JSONDecodeError:
            self.fail('invalid response')

        self.assertIn('jwt', resp)

        new_data = jwt.get_unverified_claims(resp['jwt'])

        self.assertGreater(new_data['exp'], data['exp'])
