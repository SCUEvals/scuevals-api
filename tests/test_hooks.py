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

    def test_skip_test(self):
        hooks.skip_test(transaction)

    def test_auth_api_key(self):
        hooks.auth_api_key(transaction)

    def test_class_details(self):
        hooks.class_details(transaction)

    def test_courses(self):
        hooks.courses(transaction)

    def test_post_course(self):
        hooks.post_course(transaction)

    def test_course_details(self):
        hooks.course_details(transaction)

    def test_evaluations(self):
        hooks.evaluations(transaction)

    def test_evaluation(self):
        hooks.evaluation(transaction)

    def test_evaluations_submit(self):
        hooks.evaluations_submit(transaction)

    def test_evaluations_delete(self):
        hooks.evaluations_delete(transaction)

    def test_evaluation_votes_add(self):
        hooks.evaluation_votes_add(transaction)

    def test_evaluation_votes_delete(self):
        hooks.evaluation_votes_delete(transaction)

    def test_evaluation_flags_add(self):
        hooks.evaluation_flags_add(transaction)

    def test_majors(self):
        hooks.majors(transaction)

    def test_professors(self):
        hooks.professors(transaction)

    def test_professor_details(self):
        hooks.professor_details(transaction)

    def test_quarters(self):
        hooks.quarters(transaction)

    def test_search(self):
        hooks.search(transaction)

    def test_student_update_info(self):
        hooks.student_update_info(transaction)

    def test_student_evaluations(self):
        hooks.student_evaluations(transaction)
