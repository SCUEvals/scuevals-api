import json

from scuevals_api.models import db
from tests.fixtures.factories import SectionFactory
from tests import TestCase, assert_valid_schema


class ClassTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.section = SectionFactory()
        db.session.flush()

    def test_class(self):
        q_id = self.section.quarter_id
        c_id = self.section.course_id
        p_id = self.section.professors[0].id

        url = '/classes/{}/{}/{}'.format(q_id, p_id, c_id)
        rv = self.client.get(url, headers=self.head_auth)
        self.assertEqual(rv.status_code, 200)
        assert_valid_schema(rv.data, 'class.json')

    def test_class_not_exists(self):
        url = '/classes/{}/{}/{}'.format(0, 0, 0)
        rv = self.client.get(url, headers=self.head_auth)
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)['message'], 'class does not exist')
