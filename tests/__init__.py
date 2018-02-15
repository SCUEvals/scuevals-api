import json
import unittest
import os
import yaml
from functools import wraps
from flask_jwt_extended import create_access_token
from jsonschema import validate, RefResolver
from vcr import VCR

from tests.fixtures.factories import StudentFactory, MajorFactory
from scuevals_api.cmd import init_db
from scuevals_api.models import db, Role, University, School
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

        ident = cls.student.to_dict()

        db.session.add(cls.student)
        db.session.commit()

        cls.jwt = create_access_token(identity=ident)

        api_ident = {
            'university_id': 1,
            'roles': [Role.API_Key]
        }

        cls.api_jwt = create_access_token(identity=api_ident)

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
        Role(id=0, name='Incomplete'),
        Role(id=1, name='StudentRead'),
        Role(id=2, name='StudentWrite'),
        Role(id=10, name='Administrator'),
        Role(id=20, name='API Key'),
        Role(id=100, name='Suspended')
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
