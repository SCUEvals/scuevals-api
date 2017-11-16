import json

from scuevals_api.models import db, Quarter, Department, Course, Section, Professor, Evaluation, Vote
from tests import TestCase


class EvaluationsTestCase(TestCase):
    def setUp(self):
        super(EvaluationsTestCase, self).setUp()

        with self.app.app_context():
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

        rv = self.client.post('/evaluations', headers=headers, data=json.dumps(data))
        self.assertEqual(rv.status_code, 201)

        with self.app.app_context():
            evaluation = Evaluation.query.filter(
                Evaluation.professor_id == 1,
                Evaluation.student_id == 0
            ).one_or_none()

            if evaluation is None:
                self.fail('evaluation was not inserted')

            self.assertEqual(data['evaluation'], evaluation.data)

    def test_post_evaluation_invalid_section(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        data = {
            'quarter_id': -1,
            'professor_id': 1,
            'course_id': -1,
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

        rv = self.client.post('/evaluations', headers=headers, data=json.dumps(data))
        self.assertEqual(422, rv.status_code)

        resp = json.loads(rv.data)
        self.assertEqual('invalid quarter/course combination', resp['message'])


class EvaluationTestCase(TestCase):
    def setUp(self):
        super(EvaluationTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Department(abbreviation='MATH', name='Mathematics', school_id=1))
            db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
            db.session.add(Section(id=1, quarter_id=1, course_id=1))
            db.session.add(Professor(id=1, first_name='Mary', last_name='Doe', university_id=1))
            db.session.add(Evaluation(id=1, student_id=0, professor_id=1, section_id=1, version=1, data={'q1': 'a1'}))
            db.session.commit()

    def test_get(self):
        rv = self.client.get('/evaluations/1', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(200, rv.status_code)

        expected = {
            'id': 1,
            'version': 1,
            'data': {
                'q1': 'a1'
            }
        }

        self.assertEqual(expected, json.loads(rv.data))

    def test_get_non_existing(self):
        rv = self.client.get('/evaluations/0', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])

    def test_put_upvote(self):
        rv = self.client.put('/evaluations/1/upvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(201, rv.status_code)

    def test_put_downvote(self):
        rv = self.client.put('/evaluations/1/downvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(201, rv.status_code)

    def test_del_upvote(self):
        with self.app.app_context():
            db.session.add(Vote(value=Vote.UPVOTE, student_id=0, evaluation_id=1))
            db.session.commit()

        rv = self.client.delete('/evaluations/1/upvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(204, rv.status_code)

    def test_del_downvote(self):
        with self.app.app_context():
            db.session.add(Vote(value=Vote.DOWNVOTE, student_id=0, evaluation_id=1))
            db.session.commit()

        rv = self.client.delete('/evaluations/1/downvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(204, rv.status_code)

    def test_put_upvote_non_existing_eval(self):
        rv = self.client.put('/evaluations/0/upvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('evaluation with the specified id not found', data['message'])

    def test_del_upvote_non_existing_eval(self):
        rv = self.client.delete('/evaluations/0/upvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('evaluation with the specified id not found', data['message'])

    def test_del_non_existing_upvote(self):
        rv = self.client.delete('/evaluations/1/upvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('vote not found', data['message'])

    def test_put_upvote_existing_downvote(self):
        with self.app.app_context():
            db.session.add(Vote(value=Vote.DOWNVOTE, student_id=0, evaluation_id=1))
            db.session.commit()

        rv = self.client.put('/evaluations/1/upvote', headers={'Authorization': 'Bearer ' + self.jwt})
        self.assertEqual(204, rv.status_code)
