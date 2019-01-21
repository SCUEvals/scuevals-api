import json
from datetime import timezone, timedelta, datetime
from urllib.parse import urlencode

from flask_jwt_extended import create_access_token

from tests.fixtures.factories import MajorFactory, StudentFactory, QuarterCurrentFactory, EvaluationFactory
from scuevals_api.models import Permission
from scuevals_api.utils import datetime_from_date
from tests import TestCase


class StudentsTestCase(TestCase):
    def setUp(self):
        super().setUp()

        m1 = MajorFactory()
        m2 = MajorFactory()

        self.patch_data = {
            'graduation_year': datetime.now().year,
            'gender': 'm',
            'majors': [m1.id, m2.id]
        }

    def test_patch(self):
        rv = self.client.patch('/students/{}'.format(self.student.id),
                               headers=self.head_auth,
                               data=json.dumps(self.patch_data))

        self.assertEqual(200, rv.status_code)

        self.assertEqual(self.patch_data['graduation_year'], self.student.graduation_year)
        self.assertEqual(self.patch_data['gender'], self.student.gender)
        self.assertEqual(self.patch_data['majors'], self.student.majors_list)

    def test_patch_incomplete(self):
        student = StudentFactory(
            majors=[MajorFactory()],
            permissions=[Permission.query.get(Permission.Incomplete)]
        )

        self.jwt = create_access_token(identity=student.to_dict())

        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        quarter = QuarterCurrentFactory()

        rv = self.client.patch('/students/{}'.format(student.id),
                               headers=headers,
                               data=json.dumps(self.patch_data))

        self.assertEqual(200, rv.status_code)

        self.assertEqual(self.patch_data['graduation_year'], student.graduation_year)
        self.assertEqual(self.patch_data['gender'], student.gender)
        self.assertEqual(self.patch_data['majors'], student.majors_list)

        self.assertIn(Permission.WriteEvaluations, student.permissions_list)
        self.assertIn(Permission.ReadEvaluations, student.permissions_list)
        self.assertEqual(
            datetime_from_date(quarter.period.upper + timedelta(days=1, hours=11), tzinfo=timezone.utc),
            student.read_access_until
        )

    def test_patch_wrong_user(self):
        rv = self.client.patch('/students/2', headers=self.head_auth, data=json.dumps(self.patch_data))
        self.assertEqual(rv.status_code, 403)

    def test_patch_invalid_majors(self):
        self.patch_data['majors'] = [-1]

        rv = self.client.patch(
            '/students/{}'.format(0), headers=self.head_auth, data=json.dumps(self.patch_data)
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
