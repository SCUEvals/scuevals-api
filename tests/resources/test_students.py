import json
from urllib.parse import urlencode

from flask_jwt_extended import create_access_token
# from datetime import datetime, timezone
from tests.fixtures.factories import MajorFactory, StudentFactory, QuarterFactory, EvaluationFactory
from scuevals_api.models import Permission
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

        self.student = StudentFactory(
            majors=[MajorFactory()],
            permissions=[Permission.query.get(Permission.Incomplete)]
        )

        ident = self.student.to_dict()
        self.jwt = create_access_token(identity=ident)

    def test_patch(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        QuarterFactory(current=True, period='[2018-01-01, 2018-02-01)')

        rv = self.client.patch('/students/{}'.format(self.student.id),
                               headers=headers,
                               data=json.dumps(self.patch_data))

        self.assertEqual(rv.status_code, 200)

        self.assertEqual(self.student.graduation_year, self.patch_data['graduation_year'])
        self.assertEqual(self.student.gender, self.patch_data['gender'])
        self.assertEqual(self.student.majors_list, self.patch_data['majors'])

        self.assertIn(Permission.WriteEvaluations, self.student.permissions_list)
        # self.assertIn(Permission.Read, self.student.permissions_list)
        # self.assertEqual(datetime(2018, 2, 2, tzinfo=timezone.utc), self.student.read_access_until)

    def test_patch_wrong_user(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.patch('/students/2', headers=headers, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 403)

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


class StudentEvaluations(TestCase):
    def test_get(self):
        EvaluationFactory(student=self.student)
        EvaluationFactory(student=self.student)
        EvaluationFactory()

        rv = self.client.get('/students/{}/evaluations'.format(self.student.id),
                             headers=self.head_auth,
                             query_string=urlencode({'embed': ['professor', 'course']}, True))

        self.assertEqual(200, rv.status_code)
        evals = json.loads(rv.data)
        self.assertEqual(2, len(evals))

    def test_get_wrong_user(self):
        student = StudentFactory()

        rv = self.client.get('/students/{}/evaluations'.format(student.id), headers=self.head_auth)
        self.assertEqual(rv.status_code, 403)
