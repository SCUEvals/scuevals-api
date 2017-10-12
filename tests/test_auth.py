import json
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

        self.assertEqual(rv.status_code, 200)
