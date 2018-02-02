import json
from flask_jwt_extended import create_access_token

from tests.fixtures.factories import MajorFactory, StudentFactory
from scuevals_api.models import db, Role
from tests import TestCase


class StudentsTestCase(TestCase):
    def setUp(self):
        super(StudentsTestCase, self).setUp()

        self.patch_data = {
            'graduation_year': 2018,
            'gender': 'm',
            'majors': [1, 2]
        }

        MajorFactory()
        MajorFactory()

        self.student = StudentFactory(roles=[Role.query.get(Role.Incomplete)])
        db.session.flush()

        ident = self.student.to_dict()
        self.jwt = create_access_token(identity=ident)

    def test_patch(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.patch('/students/{}'.format(self.student.id), headers=headers, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 200)

        self.assertEqual(self.student.graduation_year, self.patch_data['graduation_year'])
        self.assertEqual(self.student.gender, self.patch_data['gender'])
        self.assertEqual(self.student.majors_list, self.patch_data['majors'])

    def test_patch_wrong_user(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.patch('/students/2', headers=headers, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 401)

    def test_patch_invalid_majors(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        self.patch_data['majors'] = [-1]

        rv = self.client.patch(
            '/students/{}'.format(self.student.id), headers=headers, data=json.dumps(self.patch_data)
        )
        self.assertEqual(rv.status_code, 422)
        resp = json.loads(rv.data)
        self.assertEqual('invalid major(s) specified', resp['message'])
