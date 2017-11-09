import unittest
import os
from unittest import mock

from scuevals_api import create_app


class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        create_app()

    def test_create_app_no_env_config(self):
        del os.environ['FLASK_CONFIG']
        self.assertRaisesRegex(ValueError, 'FLASK_CONFIG env var not set', create_app)

    def test_create_app_invalid_env_config(self):
        os.environ['FLASK_CONFIG'] = 'foo'
        self.assertRaisesRegex(ValueError, 'invalid config specified', create_app)

    @mock.patch('rollbar.init_app', create=True, return_value=True)
    def test_create_app_production(self, init_app_func):
        os.environ['FLASK_CONFIG'] = 'production'
        os.environ['DATABASE_URL'] = os.environ['TEST_DATABASE_URL']
        create_app()
