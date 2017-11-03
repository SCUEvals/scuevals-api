import unittest
import os
import yaml
from functools import wraps
from flask_jwt_extended import create_access_token
from vcr import VCR

from scuevals_api.cmd import init_db, seed_db
from scuevals_api.models import db, Student, Role
from scuevals_api import create_app


fixtures_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures')

vcr = VCR(
    cassette_library_dir=os.path.join(fixtures_path, 'cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml')
)


class TestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.testing = True

        self.appx = app
        self.app = app.test_client()

        with app.app_context():
            db.drop_all()
            init_db(app, db)
            seed_db(db)

            student = Student(
                id=0,
                email='jdoe@scu.edu',
                first_name='John',
                last_name='Doe',
                roles=[Role.query.get(Role.Student)],
                university_id=1
            )

            ident = student.to_dict()

            db.session.add(student)
            db.session.commit()

            self.jwt = create_access_token(identity=ident)

            api_ident = {
                'university_id': 1,
                'roles': [Role.API_Key]
            }

            self.api_jwt = create_access_token(identity=api_ident)

    def tearDown(self):
        with self.appx.app_context():
            db.session.remove()
            db.drop_all()


def use_data(file):
    def use_data_decorator(f):
        @wraps(f)
        def wrapper(*args):
            with open(os.path.join(fixtures_path, 'data', file), 'r') as stream:
                data = yaml.load(stream)
            args = args + (data, )

            return f(*args)
        return wrapper
    return use_data_decorator
