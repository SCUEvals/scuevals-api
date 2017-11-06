import unittest

import os

from scuevals_api import create_app


class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        create_app()

    def test_create_app_no_env_config(self):
        del os.environ['FLASK_CONFIG']
        create_app()

    def test_create_app_invalid_env_config(self):
        os.environ['FLASK_CONFIG'] = 'foo'
        self.assertRaisesRegex(ValueError, 'invalid config specified', create_app)

    def test_create_app_production(self):
        os.environ['FLASK_CONFIG'] = 'production'
        create_app()
