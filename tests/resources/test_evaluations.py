import json

from tests.fixtures.factories import SectionFactory, EvaluationFactory
from scuevals_api.models import db, Quarter, Department, Course, Section, Professor, Evaluation, Vote, Student
from tests import TestCase, assert_valid_schema


class EvaluationsTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.section = SectionFactory()
        EvaluationFactory(student=self.student)
        EvaluationFactory(student=self.student)

    def test_get(self):
        rv = self.client.get('/evaluations', headers=self.head_auth)
        self.assertEqual(200, rv.status_code)
        evals = json.loads(rv.data)
        self.assertEqual(2, len(evals))
        assert_valid_schema(rv.data, 'evaluations.json')

    def test_post_evaluation(self):
        data = {
            'quarter_id': self.section.quarter_id,
            'professor_id': self.section.professors[0].id,
            'course_id': self.section.course_id,
            'display_grad_year': True,
            'display_majors': False,
            'evaluation': {
                'attitude': 1,
                'availability': 1,
                'clarity': 1,
                'difficulty': 1,
                'grading_speed': 1,
                'recommended': 1,
                'resourcefulness': 1,
                'workload': 1,
                'comment': 'Test'
            }
        }

        rv = self.client.post('/evaluations', headers=self.head_auth, data=json.dumps(data))
        self.assertEqual(201, rv.status_code)

        evaluation = Evaluation.query.filter(
            Evaluation.professor_id == self.section.professors[0].id,
            Evaluation.student_id == 0
        ).one_or_none()

        if evaluation is None:
            self.fail('evaluation was not inserted')

        self.assertEqual(data['evaluation'], evaluation.data)

    def test_post_evaluation_duplicate(self):
        data = {
            'quarter_id': self.section.quarter_id,
            'professor_id': self.section.professors[0].id,
            'course_id': self.section.course_id,
            'display_grad_year': True,
            'display_majors': False,
            'evaluation': {
                'attitude': 1,
                'availability': 1,
                'clarity': 1,
                'difficulty': 1,
                'grading_speed': 1,
                'recommended': 1,
                'resourcefulness': 1,
                'workload': 1,
                'comment': 'Test'
            }
        }

        rv = self.client.post('/evaluations', headers=self.head_auth, data=json.dumps(data))
        self.assertEqual(201, rv.status_code)

        rv = self.client.post('/evaluations', headers=self.head_auth, data=json.dumps(data))
        self.assertEqual(409, rv.status_code)

    def test_post_evaluation_invalid_section(self):
        headers = {
            'Authorization': 'Bearer ' + self.jwt,
            'Content-Type': 'application/json'
        }

        data = {
            'quarter_id': -1,
            'professor_id': self.section.professors[0].id,
            'course_id': -1,
            'display_grad_year': True,
            'display_majors': False,
            'evaluation': {
                'attitude': 1,
                'availability': 1,
                'clarity': 1,
                'difficulty': 1,
                'grading_speed': 1,
                'recommended': 1,
                'resourcefulness': 1,
                'workload': 1,
                'comment': 'Test'
            }
        }

        rv = self.client.post('/evaluations', headers=headers, data=json.dumps(data))
        self.assertEqual(422, rv.status_code)

        resp = json.loads(rv.data)
        self.assertEqual('invalid quarter/course/professor combination', resp['message'])


class EvaluationTestCase(TestCase):
    def setUp(self):
        super().setUp()

        db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                               period='[2017-01-01, 2017-02-01]', university_id=1))
        db.session.add(Department(id=1, abbreviation='MATH', name='Mathematics', school_id=1))
        db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
        db.session.add(Section(id=1, quarter_id=1, course_id=1))
        db.session.add(Professor(id=1, first_name='Mary', last_name='Doe', university_id=1))
        db.session.add(Evaluation(
            id=1, student_id=0, professor_id=1, section_id=1, version=1, data={'q1': 'a1'},
            display_grad_year=True, display_majors=False
        ))
        db.session.add(Vote(student_id=0, evaluation_id=1, value=Vote.UPVOTE))

    def test_get(self):
        rv = self.client.get('/evaluations/1', headers=self.head_auth)
        self.assertEqual(200, rv.status_code)

        expected = {
            'id': 1,
            'version': 1,
            'votes_score': 1,
            'data': {
                'q1': 'a1'
            }
        }

        self.assertEqual(expected, json.loads(rv.data))

    def test_get_non_existing(self):
        rv = self.client.get('/evaluations/0', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])


class TestEvaluationVoteTestCase(TestCase):
    def setUp(self):
        super().setUp()
        qs = Quarter.query.all()
        db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                               period='[2017-01-01, 2017-02-01]', university_id=1))
        db.session.add(Department(id=1, abbreviation='MATH', name='Mathematics', school_id=1))
        db.session.add(Course(id=1, title='Math Course', number='1', department_id=1))
        db.session.add(Section(id=1, quarter_id=1, course_id=1))
        db.session.add(Professor(id=1, first_name='Mary', last_name='Doe', university_id=1))
        db.session.add(Student(id=1, email='sdoe@scu.edu', first_name='Sandra', last_name='Doe', university_id=1))
        db.session.add(Evaluation(id=1, student_id=1, professor_id=1, section_id=1, version=1, data={'q1': 'a1'}))
        db.session.add(Evaluation(id=2, student_id=0, professor_id=1, section_id=1, version=1, data={'q1': 'a1'}))

    def test_put_upvote(self):
        rv = self.client.put('/evaluations/1/vote', headers=self.head_auth, data=json.dumps({'value': 'u'}))
        self.assertEqual(201, rv.status_code)

        votes = Evaluation.query.get(1).votes
        self.assertEqual(1, len(votes))
        self.assertEqual(Vote.UPVOTE, votes[0].value)

    def test_put_downvote(self):
        rv = self.client.put('/evaluations/1/vote', headers=self.head_auth, data=json.dumps({'value': 'd'}))
        self.assertEqual(201, rv.status_code)

        votes = Evaluation.query.get(1).votes
        self.assertEqual(1, len(votes))
        self.assertEqual(Vote.DOWNVOTE, votes[0].value)

    def test_put_upvote_existing_downvote(self):
        db.session.add(Vote(value=Vote.DOWNVOTE, student_id=0, evaluation_id=1))

        rv = self.client.put('/evaluations/1/vote', headers=self.head_auth, data=json.dumps({'value': 'u'}))
        self.assertEqual(204, rv.status_code)

        votes = Evaluation.query.get(1).votes
        self.assertEqual(1, len(votes))
        self.assertEqual(Vote.UPVOTE, votes[0].value)

    def test_put_vote_non_existing_eval(self):
        rv = self.client.put('/evaluations/0/vote', headers=self.head_auth, data=json.dumps({'value': 'u'}))
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('evaluation with the specified id not found', data['message'])

    def test_put_vote_own_evaluation(self):
        rv = self.client.put('/evaluations/2/vote', headers=self.head_auth, data=json.dumps({'value': 'u'}))
        self.assertEqual(403, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not allowed to vote on your own evaluations', data['message'])

    def test_del_vote(self):
        db.session.add(Vote(value=Vote.UPVOTE, student_id=0, evaluation_id=1))

        rv = self.client.delete('/evaluations/1/vote', headers=self.head_auth)
        self.assertEqual(204, rv.status_code)

        votes = Evaluation.query.get(1).votes
        self.assertEqual(0, len(votes))

    def test_del_vote_non_existing_eval(self):
        rv = self.client.delete('/evaluations/0/vote', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('evaluation with the specified id not found', data['message'])

    def test_del_non_existing_vote(self):
        rv = self.client.delete('/evaluations/1/vote', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('vote not found', data['message'])
