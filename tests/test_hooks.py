import unittest

from tests.dredd.hooks import before_all, before_each, after_each, course_details

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
        before_all(transaction)

    def setUp(self):
        before_each(transaction)

    def tearDown(self):
        after_each(transaction)

    def test_course_details(self):
        course_details(transaction)
