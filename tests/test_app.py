import unittest
import os
from unittest import mock

from scuevals_api import create_app


@mock.patch.dict(os.environ, os.environ)
class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        os.environ['DATABASE_URL'] = os.environ['TEST_DATABASE_URL']
        create_app()

    @mock.patch('scuevals_api.errors.rollbar.init_app', create=True, return_value=True)
    def test_create_app_production(self, rollbar_init_func):
        os.environ['DATABASE_URL'] = os.environ['TEST_DATABASE_URL']
        os.environ['ROLLBAR_API_KEY'] = ''
        create_app('production')
        self.assertTrue(rollbar_init_func.called)
