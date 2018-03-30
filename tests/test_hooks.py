import unittest

from tests.dredd import hooks

transaction = {
    'request': {
        'headers': {
            'Authorization': ''
        }
    }
}


class HooksTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        hooks.before_all(transaction)

    def setUp(self):
        hooks.before_each(transaction)

    def tearDown(self):
        hooks.after_each(transaction)

    def test_course_details(self):
        hooks.course_details(transaction)

    def test_evaluations(self):
        hooks.evaluations(transaction)

    def test_evaluation(self):
        hooks.evaluation(transaction)

    def test_professor_details(self):
        hooks.professor_details(transaction)

    def test_student_evaluations(self):
        hooks.student_evaluations(transaction)
