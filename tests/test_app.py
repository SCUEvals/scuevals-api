import unittest
import os
from unittest import mock

from scuevals_api import create_app


@mock.patch.dict(os.environ, os.environ)
class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        create_app()

    @mock.patch('rollbar.init_app', create=True, return_value=True)
    def test_create_app_production(self, init_app_func):
        os.environ['DATABASE_URL'] = os.environ['TEST_DATABASE_URL']
        create_app('production')
