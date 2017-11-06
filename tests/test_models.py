from scuevals_api.models import Student, Role, db, Major
from tests import TestCase


class StudentTestCase(TestCase):

    def test_roles_list(self):
        with self.appx.app_context():
            student = Student.query.get(0)
            student.roles_list = [Role.Student]
            self.assertEqual(student.roles_list, [1])
            student.roles_list = []
            self.assertEqual(student.roles_list, [])

    def test_roles_list_invalid_role(self):
        with self.appx.app_context():
            student = Student.query.get(0)
            with self.assertRaisesRegex(ValueError, 'role does not exist'):
                student.roles_list = [-1]

    def test_majors_list(self):
        with self.appx.app_context():
            db.session.add(Major(id=1, university_id=1, name='Major1'))
            student = Student.query.get(0)
            student.majors_list = [1]
            self.assertEqual(student.majors_list, [1])
            student.majors_list = []
            self.assertEqual(student.majors_list, [])

    def test_majors_list_invalid_major(self):
        with self.appx.app_context():
            student = Student.query.get(0)
            with self.assertRaisesRegex(ValueError, 'major does not exist'):
                student.majors_list = [1]
