import unittest
import os
import yaml
from functools import wraps
from cmd import init_db, seed_db
from models import db
from scuevals_api import create_app


class TestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DATABASE_URL']
        app.testing = True
        self.appx = app
        self.app = app.test_client()

        with app.app_context():
            init_db(app, db)
            seed_db(db)

    def tearDown(self):
        with self.appx.app_context():
            db.session.remove()
            db.drop_all()


def use_data(file):
    def use_data_decorator(f):
        @wraps(f)
        def wrapper(*args):
            with open(os.path.join('fixtures/data', file), 'r') as stream:
                data = yaml.load(stream)
            args = args + (data, )

            return f(*args)
        return wrapper
    return use_data_decorator
