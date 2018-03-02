from scuevals_api.models import Role
from tests import TestCase
from tests.fixtures.factories import UserFactory


class UserTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()

    def test_roles_list(self):
        self.user.roles_list = [Role.Read]
        self.assertEqual(self.user.roles_list, [1])
        self.user.roles_list = []
        self.assertEqual(self.user.roles_list, [])

    def test_roles_list_invalid_role(self):
        with self.assertRaisesRegex(ValueError, 'role does not exist'):
            self.user.roles_list = [-1]
