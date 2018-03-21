import unittest

from tests.dredd.hooks import before_all, before_each, after_each

transaction = {
    'request': {
        'headers': {
            'Authorization': ''
        }
    }
}


class HooksTestCase(unittest.TestCase):
    def test_hooks(self):
        before_all(transaction)
        before_each(transaction)
        after_each(transaction)
