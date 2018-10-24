import json

from tests import TestCase, use_data
from tests.fixtures.factories import OfficialUserTypeFactory


class OfficialUserTypesCase(TestCase):
    def setUp(self):
        super().setUp()

        self.headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

    @use_data('official_user_types.yaml')
    def test_post(self, data):
        out = OfficialUserTypeFactory(email='jdoe2@scu.edu', type='misc')

        rv = self.client.post('/official_user_types', headers=self.headers, data=data['official_user_types'])
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual(2, resp['updated_count'])

        self.session.refresh(out)
        self.assertEqual('professor', out.type)
