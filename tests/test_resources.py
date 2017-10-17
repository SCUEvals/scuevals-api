from urllib.parse import urlencode
from flask import json
from helper import TestCase
from models import db, Major, Student, Professor, Course, Department


class StudentsTestCase(TestCase):

    def setUp(self):
        super(StudentsTestCase, self).setUp()

        with self.appx.app_context():
            db.session.add(Major(id=1, university_id=1, name='Major1'))
            db.session.add(Major(id=2, university_id=1, name='Major2'))
            db.session.commit()

    def test_students_patch(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        data = {
            'graduation_year': 2018,
            'gender': 'm',
            'majors': [1, 2]
        }

        rv = self.app.patch('/students/0', headers=headers, data=json.dumps(data))
        self.assertEqual(rv.status_code, 200)

        with self.appx.app_context():
            student = Student.query.get(0)
            self.assertEqual(student.graduation_year, data['graduation_year'])
            self.assertEqual(student.gender, data['gender'])
            self.assertEqual(student.majors_list, data['majors'])


class SearchTestCase(TestCase):
    def setUp(self):
        super(SearchTestCase, self).setUp()

        with self.appx.app_context():
            db.session.add(Professor(first_name='Mathias', last_name='Doe', university_id=1))
            db.session.add(Department(abbreviation='MATH', name='Mathematics', school_id=1))
            db.session.add(Course(title='Math Course', number='1', department_id=1))
            db.session.commit()

    def test_search(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        rv = self.app.get('/search', headers=headers, query_string=urlencode({'q': 'mat'}))

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertIn('courses', data)
        self.assertIn('professors', data)
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(len(data['professors']), 1)
