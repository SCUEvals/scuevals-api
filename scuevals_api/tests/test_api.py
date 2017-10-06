import tempfile
import unittest
import os
from cmd import init_db, seed_db
from scuevals_api import create_app
from scuevals_api.models import db


class APITestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()

        with app.app_context():
            init_db(app, db)
            seed_db(db)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])
