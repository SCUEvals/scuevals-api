from tests.fixtures.factories import MajorFactory, StudentFactory
from tests import TestCase


class StudentTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.student = StudentFactory()

    def test_majors_list(self):
        MajorFactory(id=1000)
        self.student.majors_list = [1000]
        self.assertEqual(self.student.majors_list, [1000])
        self.student.majors_list = []
        self.assertEqual(self.student.majors_list, [])

    def test_majors_list_invalid_major(self):
        with self.assertRaisesRegex(ValueError, 'major does not exist'):
            self.student.majors_list = [-1]
