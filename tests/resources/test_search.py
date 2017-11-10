import json
from urllib.parse import urlencode

from scuevals_api.models import db, Professor, Department, Course
from tests import TestCase


class SearchTestCase(TestCase):
    def setUp(self):
        super(SearchTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Professor(first_name='Mathias', last_name='Doe', university_id=1))
            db.session.add(Department(abbreviation='MATH', name='Mathematics', school_id=1))
            db.session.add(Course(title='Math Course', number='1', department_id=1))
            db.session.commit()

    def test_search(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt
        }

        rv = self.client.get('/search', headers=headers, query_string=urlencode({'q': 'mat'}))
        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertIn('courses', data)
        self.assertIn('professors', data)
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(len(data['professors']), 1)
