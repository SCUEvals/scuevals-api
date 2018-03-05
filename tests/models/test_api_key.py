from scuevals_api.models import Permission
from tests import TestCase
from tests.fixtures.factories import APIKeyFactory


class APIKeyTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.api_key = APIKeyFactory()

    def test_permissions_list(self):
        self.api_key.permissions_list = [Permission.UpdateMajors]
        self.assertEqual(self.api_key.permissions_list, [Permission.UpdateMajors])
        self.api_key.permissions_list = []
        self.assertEqual(self.api_key.permissions_list, [])

    def test_permissions_list_invalid_permission(self):
        with self.assertRaisesRegex(ValueError, 'permission does not exist'):
            self.api_key.permissions_list = [-1]
