import json
from datetime import datetime, timezone, date
from urllib.parse import urlencode

from flask_jwt_extended import create_access_token
from freezegun import freeze_time
from psycopg2.extras import DateRange

from tests.fixtures.factories import (
    SectionFactory, EvaluationFactory, VoteFactory, QuarterFactory, StudentFactory, ReasonFactory
)
from scuevals_api.models import db, Evaluation, Vote, Permission
from tests import TestCase, assert_valid_schema


class EvaluationsTestCase(TestCase):
    def setUp(self):
        super().setUp()

        QuarterFactory(period=DateRange(date(2018, 1, 1), date(2018, 2, 1)))
        self.section = SectionFactory()

    def test_get(self):
        EvaluationFactory()
        EvaluationFactory()
        EvaluationFactory()

        rv = self.client.get('/evaluations',
                             headers=self.head_auth,
                             query_string=urlencode({'embed': ['professor', 'course']}, True))

        self.assertEqual(200, rv.status_code)
        evals = json.loads(rv.data)
        self.assertEqual(3, len(evals))

    def test_get_quarter_id(self):
        ev = EvaluationFactory()
        EvaluationFactory()

        rv = self.client.get('/evaluations',
                             headers=self.head_auth,
                             query_string=urlencode({'quarter_id': ev.section.quarter_id}))

        self.assertEqual(200, rv.status_code)
        evals = json.loads(rv.data)
        self.assertEqual(1, len(evals))

    def test_get_professor_id(self):
        ev = EvaluationFactory()
        EvaluationFactory()

        rv = self.client.get('/evaluations',
                             headers=self.head_auth,
                             query_string=urlencode({'professor_id': ev.professor_id}))

        self.assertEqual(200, rv.status_code)
        evals = json.loads(rv.data)
        self.assertEqual(1, len(evals))

    def test_get_course_id(self):
        ev = EvaluationFactory()
        EvaluationFactory()

        rv = self.client.get('/evaluations',
                             headers=self.head_auth,
                             query_string=urlencode({'course_id': ev.section.course_id}))

        self.assertEqual(200, rv.status_code)
        evals = json.loads(rv.data)
        self.assertEqual(1, len(evals))

    @freeze_time('2018-01-05')
    def test_post_evaluation(self):
        student = StudentFactory(permissions=[Permission.query.get(Permission.WriteEvaluations)])
        db.session.flush()
        jwt = create_access_token(identity=student.to_dict())
        headers = {'Authorization': 'Bearer ' + jwt, 'Content-Type': 'application/json'}

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
                'easiness': 1,
                'grading_speed': 1,
                'recommended': 1,
                'resourcefulness': 1,
                'workload': 1,
                'comment': 'Test'
            }
        }

        rv = self.client.post('/evaluations', headers=headers, data=json.dumps(data))
        self.assertEqual(201, rv.status_code)

        resp = json.loads(rv.data)
        self.assertIn('jwt', resp)
        self.assertNotEqual('', resp['jwt'])

        evaluation = Evaluation.query.filter(
            Evaluation.professor_id == self.section.professors[0].id,
            Evaluation.student_id == student.id
        ).one_or_none()

        if evaluation is None:
            self.fail('evaluation was not inserted')

        self.assertEqual(data['evaluation'], evaluation.data)

        self.assertIn(Permission.ReadEvaluations, student.permissions_list)
        self.assertIn(Permission.VoteOnEvaluations, student.permissions_list)
        self.assertEqual(datetime(2018, 2, 2, 0, 0, tzinfo=timezone.utc), student.read_access_until)

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
                'easiness': 1,
                'grading_speed': 1,
                'recommended': 1,
                'resourcefulness': 1,
                'workload': 1,
                'comment': 'Test'
            }
        }

        EvaluationFactory(
            section=self.section,
            professor=self.section.professors[0],
            student=self.student
        )

        rv = self.client.post('/evaluations', headers=self.head_auth_json, data=json.dumps(data))
        self.assertEqual(409, rv.status_code)

    def test_post_evaluation_invalid_section(self):
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
                'easiness': 1,
                'grading_speed': 1,
                'recommended': 1,
                'resourcefulness': 1,
                'workload': 1,
                'comment': 'Test'
            }
        }

        rv = self.client.post('/evaluations', headers=self.head_auth_json, data=json.dumps(data))
        self.assertEqual(422, rv.status_code)

        resp = json.loads(rv.data)
        self.assertEqual('invalid quarter/course/professor combination', resp['message'])


class EvaluationsRecentTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.recent_evals = [EvaluationFactory(), EvaluationFactory()]
        EvaluationFactory()

        db.session.flush()

    def test_get(self):
        rv = self.client.get('/evaluations/recent', headers=self.head_auth, query_string=urlencode({'count': 2}))
        self.assertEqual(200, rv.status_code)
        assert_valid_schema(rv.data, 'evaluations.json')

        evals = json.loads(rv.data)
        self.assertEqual(2, len(evals))
        self.assertEqual(self.recent_evals[0].id, evals[0]['id'])
        self.assertEqual(self.recent_evals[1].id, evals[1]['id'])

    def test_get_no_count(self):
        rv = self.client.get('/evaluations/recent', headers=self.head_auth)
        self.assertEqual(200, rv.status_code)
        assert_valid_schema(rv.data, 'evaluations.json')

        evals = json.loads(rv.data)
        self.assertEqual(3, len(evals))


class EvaluationTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.section = SectionFactory()
        self.eval = EvaluationFactory(student=self.student)
        self.eval2 = EvaluationFactory(section=self.section, professor=self.section.professors[0])
        eval3 = EvaluationFactory(student=self.student)
        VoteFactory(student_id=0, evaluation=eval3)

    def test_get(self):
        rv = self.client.get('/evaluations/{}'.format(self.eval.id), headers=self.head_auth)
        self.assertEqual(200, rv.status_code)

        assert_valid_schema(rv.data, 'evaluation.json')

    def test_get_non_existing(self):
        rv = self.client.get('/evaluations/0', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not found', data['message'])

    def test_delete(self):
        rv = self.client.delete('/evaluations/{}'.format(self.eval.id), headers=self.head_auth)
        self.assertEqual(204, rv.status_code)

        ev = Evaluation.query.get(self.eval.id)
        self.assertIsNone(ev)

    def test_delete_other_student(self):
        rv = self.client.delete('/evaluations/{}'.format(self.eval2.id), headers=self.head_auth)
        self.assertEqual(403, rv.status_code)

    def test_delete_invalid_eval(self):
        rv = self.client.delete('/evaluations/999', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)

    def test_delete_with_vote(self):
        VoteFactory(evaluation=self.eval, student=self.student)
        rv = self.client.delete('/evaluations/{}'.format(self.eval.id), headers=self.head_auth)
        self.assertEqual(204, rv.status_code)

        ev = Evaluation.query.get(self.eval.id)
        self.assertIsNone(ev)


class EvaluationVoteTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.section = SectionFactory()
        self.eval = EvaluationFactory(student=self.student)
        self.eval2 = EvaluationFactory()
        EvaluationFactory(student=self.student)

        db.session.flush()

    def test_put_upvote(self):
        rv = self.client.put('/evaluations/{}/vote'.format(self.eval2.id),
                             headers=self.head_auth,
                             data=json.dumps({'value': 'u'}))

        self.assertEqual(204, rv.status_code)

        self.assertEqual(1, len(self.eval2.votes))
        self.assertEqual(Vote.UPVOTE, self.eval2.votes[0].value)

    def test_put_downvote(self):
        rv = self.client.put('/evaluations/{}/vote'.format(self.eval2.id),
                             headers=self.head_auth,
                             data=json.dumps({'value': 'd'}))

        self.assertEqual(204, rv.status_code)

        self.assertEqual(1, len(self.eval2.votes))
        self.assertEqual(Vote.DOWNVOTE, self.eval2.votes[0].value)

    def test_put_upvote_existing_downvote(self):
        VoteFactory(value=Vote.DOWNVOTE, student=self.student, evaluation=self.eval2)

        rv = self.client.put('/evaluations/{}/vote'.format(self.eval2.id),
                             headers=self.head_auth,
                             data=json.dumps({'value': 'u'}))

        self.assertEqual(204, rv.status_code)

        self.assertEqual(1, len(self.eval2.votes))
        self.assertEqual(Vote.UPVOTE, self.eval2.votes[0].value)

    def test_put_vote_non_existing_eval(self):
        rv = self.client.put('/evaluations/0/vote', headers=self.head_auth, data=json.dumps({'value': 'u'}))
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('evaluation with the specified id not found', data['message'])

    def test_put_vote_own_evaluation(self):
        rv = self.client.put('/evaluations/{}/vote'.format(self.eval.id),
                             headers=self.head_auth,
                             data=json.dumps({'value': 'u'}))

        self.assertEqual(403, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not allowed to vote on your own evaluations', data['message'])

    def test_del_vote(self):
        VoteFactory(student=self.student, evaluation=self.eval2)

        rv = self.client.delete('/evaluations/{}/vote'.format(self.eval2.id), headers=self.head_auth)
        self.assertEqual(204, rv.status_code)

        self.assertEqual(0, len(self.eval2.votes))

    def test_del_vote_non_existing_eval(self):
        rv = self.client.delete('/evaluations/0/vote', headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('evaluation with the specified id not found', data['message'])

    def test_del_non_existing_vote(self):
        rv = self.client.delete('/evaluations/{}/vote'.format(self.eval2.id), headers=self.head_auth)
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('vote not found', data['message'])


class EvaluationFlagTestCase(TestCase):
    def setUp(self):
        self.reason1 = ReasonFactory()
        self.reason2 = ReasonFactory()

        db.session.flush()

        self.post_data = {
            'reason_ids': [self.reason1.id, self.reason2.id],
            'comment': 'Foo'
        }

    def test_post_flag(self):
        evaluation = EvaluationFactory()
        db.session.flush()

        rv = self.client.post('/evaluations/{}/flag'.format(evaluation.id),
                              headers=self.head_auth_json,
                              data=json.dumps(self.post_data))

        self.assertEqual(201, rv.status_code)

        flags = evaluation.flags
        self.assertEqual(1, len(flags))

    def test_post_flag_no_comment(self):
        evaluation = EvaluationFactory()
        db.session.flush()

        data = self.post_data
        del data['comment']

        rv = self.client.post('/evaluations/{}/flag'.format(evaluation.id),
                              headers=self.head_auth_json,
                              data=json.dumps(self.post_data))

        self.assertEqual(201, rv.status_code)

    def test_post_flag_duplicate(self):
        evaluation = EvaluationFactory()
        db.session.flush()

        rv = self.client.post('/evaluations/{}/flag'.format(evaluation.id),
                              headers=self.head_auth_json,
                              data=json.dumps(self.post_data))

        self.assertEqual(201, rv.status_code)

        rv = self.client.post('/evaluations/{}/flag'.format(evaluation.id),
                              headers=self.head_auth_json,
                              data=json.dumps(self.post_data))

        self.assertEqual(409, rv.status_code)

    def test_post_flag_non_existing_eval(self):
        rv = self.client.post('/evaluations/0/flag', headers=self.head_auth, data=json.dumps(self.post_data))
        self.assertEqual(404, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('evaluation with the specified id not found', data['message'])

    def test_post_flag_own_evaluation(self):
        evaluation = EvaluationFactory(student=self.student)
        db.session.flush()

        rv = self.client.post('/evaluations/{}/flag'.format(evaluation.id),
                              headers=self.head_auth_json,
                              data=json.dumps(self.post_data))

        self.assertEqual(403, rv.status_code)
        data = json.loads(rv.data)
        self.assertIn('not allowed to flag your own evaluations', data['message'])

    def test_post_flag_invalid_reason(self):
        evaluation = EvaluationFactory()
        db.session.flush()

        data = {
            'reason_ids': [-1],
            'comment': 'Foo'
        }

        rv = self.client.post('/evaluations/{}/flag'.format(evaluation.id),
                              headers=self.head_auth_json,
                              data=json.dumps(data))

        self.assertEqual(422, rv.status_code)
