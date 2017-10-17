import unittest
import os
import yaml
from functools import wraps
from flask_jwt_simple import create_jwt
from cmd import init_db, seed_db
from models import db, Student, Role
from scuevals_api import create_app


class TestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DATABASE_URL']
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

            self.jwt = create_jwt(identity=ident)

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
