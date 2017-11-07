import json

from scuevals_api.models import db, School, Department
from tests import TestCase, use_data


class DepartmentsTestCase(TestCase):
    def setUp(self):
        super(DepartmentsTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(School(id=0, abbreviation='ARTS', name='Arts & Sciences', university_id=1))
            db.session.add(Department(abbreviation='MATH', name='Mathematics', school_id=0))
            db.session.add(Department(abbreviation='ENGL', name='English', school_id=0))
            db.session.commit()

    def test_get(self):
        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.client.get('/departments', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)

    @use_data('departments.yaml')
    def test_post(self, data):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.post('/departments', headers=headers, data=data['departments'])
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual(74, resp['updated_count'])

    @use_data('departments.yaml')
    def test_post_invalid_school(self, data):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        rv = self.client.post('/departments', headers=headers, data=data['departments_invalid'])
        self.assertEqual(422, rv.status_code)
