from scuevals_api.models import Permission
from tests import TestCase
from tests.fixtures.factories import UserFactory


class UserTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()

    def test_permissions_list(self):
        self.user.permissions_list = [Permission.ReadEvaluations]
        self.assertEqual(self.user.permissions_list, [1])
        self.user.permissions_list = []
        self.assertEqual(self.user.permissions_list, [])

    def test_permissions_list_invalid_permission(self):
        with self.assertRaisesRegex(ValueError, 'permission does not exist'):
            self.user.permissions_list = [-1]
