import json
import logging
import unittest
import os
from contextlib import contextmanager

import yaml
from functools import wraps
from flask_jwt_extended import create_access_token
from jsonschema import validate, RefResolver
from vcr import VCR

from tests.fixtures.factories import StudentFactory, MajorFactory, APIKeyFactory
from scuevals_api.cmd import init_db
from scuevals_api.models import db, Permission, University, School, Reason
from scuevals_api import create_app

fixtures_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures')

vcr = VCR(
    cassette_library_dir=os.path.join(fixtures_path, 'cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml')
)


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.client = cls.app.test_client()

        ctx = cls.app.app_context()
        ctx.push()

        db.drop_all()
        init_db(cls.app, db)
        seed_db(db)

        cls.session = db.session

        cls.student = StudentFactory(
            id=0,
            majors=[MajorFactory()],
        )

        cls.api_key = APIKeyFactory(id=0)

        db.session.commit()

        cls.jwt = create_access_token(identity=cls.student.to_dict())
        cls.api_jwt = create_access_token(identity=cls.api_key.identity())

        # these are just shorthands to DRY up the code
        cls.head_auth = {'Authorization': 'Bearer ' + cls.jwt}
        cls.head_auth_json = cls.head_auth
        cls.head_auth_json['Content-Type'] = 'application/json'

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()


def seed_db(target):
    scu = University(id=1, abbreviation='SCU', name='Santa Clara University')

    target.session.add(scu)
    target.session.add_all([
        School(abbreviation='BUS', name='Business', university=scu),
        School(abbreviation='EGR', name='Engineering', university=scu),
        School(abbreviation='AS', name='Arts and Sciences', university=scu),
        School(abbreviation='UNV', name='Generic', university=scu),
        School(abbreviation='CPE', name='Education and Counseling Psychology', university=scu),
        School(abbreviation='LAW', name='Law', university=scu)
    ])

    db.session.add_all([
        Permission(id=0, name='Incomplete'),
        Permission(id=1, name='ReadEvaluations'),
        Permission(id=2, name='WriteEvaluations'),
        Permission(id=3, name='VoteOnEvaluations'),
        Permission(id=100, name='UpdateCourses'),
        Permission(id=101, name='UpdateDepartments'),
        Permission(id=102, name='UpdateMajors'),
        Permission(id=1000, name='Administrator'),
    ])

    db.session.add_all([
        Reason(id=0, name='Other'),
        Reason(id=1, name='Spam'),
        Reason(id=2, name='Offensive'),
        Reason(id=3, name='SensitiveInfo')
    ])

    db.session.commit()


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


@contextmanager
def no_logging():
    log_state = logging.getLogger().getEffectiveLevel()
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(log_state)


# source: https://medium.com/grammofy/testing-your-python-api-app-with-json-schema-52677fe73351
def assert_valid_schema(data, schema_file):
    """ Checks whether the given data matches the schema """

    j = json.loads(data)
    schema = _load_json_schema(schema_file)

    resolver = RefResolver('file://' + fixtures_path + '/schemas/', schema)

    return validate(j, schema, resolver=resolver)


def _load_json_schema(filename):
    """ Loads the given schema file """

    relative_path = os.path.join(fixtures_path, 'schemas', filename)
    absolute_path = os.path.join(os.path.dirname(__file__), relative_path)

    with open(absolute_path) as schema_file:
        return json.loads(schema_file.read())
