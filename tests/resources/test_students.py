import json
from flask_jwt_extended import create_access_token

from scuevals_api.models import db, Major, Student, Role
from tests import TestCase


class StudentsTestCase(TestCase):
    def setUp(self):
        super(StudentsTestCase, self).setUp()

        self.patch_data = {
            'graduation_year': 2018,
            'gender': 'm',
            'majors': [1, 2]
        }

        with self.app.app_context():
            db.session.add(Major(id=1, university_id=1, name='Major1'))
            db.session.add(Major(id=2, university_id=1, name='Major2'))

            student = Student(
                id=1,
                email='mmyers@scu.edu',
                first_name='Mike',
                last_name='Myers',
                roles=[Role.query.get(Role.Incomplete)],
                university_id=1
            )

            ident = student.to_dict()

            db.session.add(student)
            db.session.commit()

            self.jwt = create_access_token(identity=ident)

    def test_patch(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.patch('/students/1', headers=headers, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 200)

        with self.app.app_context():
            student = Student.query.get(1)
            self.assertEqual(student.graduation_year, self.patch_data['graduation_year'])
            self.assertEqual(student.gender, self.patch_data['gender'])
            self.assertEqual(student.majors_list, self.patch_data['majors'])

    def test_patch_wrong_user(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.patch('/students/2', headers=headers, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 401)

    def test_patch_non_existing_user(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        with self.app.app_context():
            db.session.delete(Student.query.get(1))
            db.session.commit()

        rv = self.client.patch('/students/1', headers=headers, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 422)
        resp = json.loads(rv.data)
        self.assertEqual('user does not exist', resp['message'])

    def test_patch_invalid_majors(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        self.patch_data['majors'] = [-1]

        rv = self.client.patch('/students/1', headers=headers, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 422)
        resp = json.loads(rv.data)
        self.assertEqual('invalid major(s) specified', resp['message'])
