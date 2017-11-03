from urllib.parse import urlencode
from flask import json
from flask_jwt_extended import create_access_token

from tests import TestCase, use_data
from scuevals_api.models import db, Major, Student, Professor, Course, Department, Quarter, Section, Role, School, \
    Evaluation


class ResourceTestCase(TestCase):
    def setUp(self):
        super(ResourceTestCase, self).setUp()

        with self.appx.app_context():
            student = Student(
                id=0,
                email='jdoe@scu.edu',
                first_name='John',
                last_name='Doe',
                university_id=1
            )
            ident = student.to_dict()
            self.jwt = create_access_token(identity=ident)

    def test_resource_no_roles(self):
        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.app.get('/quarters', headers=headers)

        self.assertEqual(rv.status_code, 401)


class QuartersTestCase(TestCase):
    def setUp(self):
        super(QuartersTestCase, self).setUp()

        with self.appx.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Quarter(id=2, year=2017, name='Spring', current=False,
                                   period='[2017-03-01, 2017-04-01]', university_id=1))
            db.session.commit()

    def test_quarters(self):
        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.app.get('/quarters', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)


class DepartmentsTestCase(TestCase):
    def setUp(self):
        super(DepartmentsTestCase, self).setUp()

        with self.appx.app_context():
            db.session.add(School(id=0, abbreviation='ARTS', name='Arts & Sciences', university_id=1))
            db.session.add(Department(abbreviation='MATH', name='Mathematics', school_id=0))
            db.session.add(Department(abbreviation='ENGL', name='English', school_id=0))
            db.session.commit()

    def test_get(self):
        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.app.get('/departments', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)

    @use_data('departments_post.yaml')
    def test_post(self, data):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        rv = self.app.post('/departments', headers=headers, data=data['departments'])
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual(74, resp['updated_count'])


class MajorsTestCase(TestCase):

    def test_majors(self):
        with self.appx.app_context():
            db.session.add(Major(id=1, university_id=1, name='Major1'))
            db.session.add(Major(id=2, university_id=1, name='Major2'))
            db.session.commit()

        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.app.get('/majors', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)

    def test_post(self):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        data = {'majors': ['Major1', 'Major2', 'Major3']}

        rv = self.app.post('/majors', headers=headers, data=json.dumps(data))
        print(rv.data)
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual('success', resp['result'])


class StudentsTestCase(TestCase):
    def setUp(self):
        super(StudentsTestCase, self).setUp()

        with self.appx.app_context():
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

        rv = self.app.patch('/students/1', headers=headers, data=json.dumps(data))
        self.assertEqual(rv.status_code, 200)

        with self.appx.app_context():
            student = Student.query.get(1)
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
            'Authorization': 'Bearer ' + self.jwt
        }

        rv = self.app.get('/search', headers=headers, query_string=urlencode({'q': 'mat'}))
        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertIn('courses', data)
        self.assertIn('professors', data)
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(len(data['professors']), 1)


class CoursesTestCase(TestCase):
    def setUp(self):
        super(CoursesTestCase, self).setUp()

        with self.appx.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Quarter(id=2, year=2017, name='Spring', current=False,
                                   period='[2017-03-01, 2017-04-01]', university_id=1))
            db.session.add(Quarter(id=3900, year=2017, name='Fall', current=False,
                                   period='[2017-05-01, 2017-06-01]', university_id=1))
            db.session.add(Department(abbreviation='ANTH', name='Anthropology', school_id=1))
            db.session.add(Department(abbreviation='COMM', name='Communications', school_id=1))
            db.session.add(Course(id=1000, title='Math Course', number='1', department_id=1))
            db.session.add(Course(id=1001, title='Arts Course', number='2', department_id=1))
            db.session.add(Section(quarter_id=1, course_id=1000))
            db.session.add(Section(quarter_id=2, course_id=1001))
            db.session.commit()

    def test_get(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
        }

        rv = self.app.get('/courses', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)

    def test_get_quarter_id(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
        }

        rv = self.app.get('/courses', headers=headers, query_string=urlencode({'quarter_id': 1}))

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 1)

    @use_data('courses_post.yaml')
    def test_post(self, data):
        headers = {
            'Authorization': 'Bearer ' + self.api_jwt,
            'Content-Type': 'application/json'
        }

        rv = self.app.post('/courses', headers=headers, data=data['courses'])
        self.assertEqual(200, rv.status_code)
        resp = json.loads(rv.data)
        self.assertEqual(21, resp['updated_count'])


class EvaluationsTestCase(TestCase):
    def setUp(self):
        super(EvaluationsTestCase, self).setUp()

        with self.appx.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Department(abbreviation='GEN', name='General', school_id=1))
            db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
            db.session.add(Section(quarter_id=1, course_id=1))
            db.session.add(Professor(id=1, first_name='Mathias', last_name='Doe', university_id=1))
            db.session.commit()

    def test_post_evaluation(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        data = {
            'quarter_id': 1,
            'professor_id': 1,
            'course_id': 1,
            'evaluation': {
                'attitude': 1,
                'availability': 1,
                'clarity': 1,
                'handwriting': 1,
                'take_again': 1,
                'timeliness': 1,
                'evenness': 1,
                'workload': 1,
                'comment': 'Test'
            }
        }

        rv = self.app.post('/evaluations', headers=headers, data=json.dumps(data))
        self.assertEqual(rv.status_code, 201)

        with self.appx.app_context():
            evaluation = Evaluation.query.filter(
                Evaluation.professor_id == 1,
                Evaluation.student_id == 0
            ).one_or_none()

            if evaluation is None:
                self.fail('evaluation was not inserted')

            self.assertEqual(data['evaluation'], evaluation.data)
