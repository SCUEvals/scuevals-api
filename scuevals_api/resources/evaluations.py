from datetime import timedelta, timezone

from flask_jwt_extended import get_jwt_identity, current_user, create_access_token
from flask_restful import Resource
from marshmallow import fields, Schema, validate
from sqlalchemy import func
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import UnprocessableEntity, NotFound, Forbidden, Conflict

from scuevals_api.models import Permission, Section, Evaluation, db, Professor, Quarter, Vote
from scuevals_api.auth import auth_required
from scuevals_api.utils import use_args, datetime_from_date


class EvaluationSchemaV1(Schema):
    attitude = fields.Int(required=True, validate=validate.Range(1, 4))
    availability = fields.Int(required=True, validate=validate.Range(1, 4))
    clarity = fields.Int(required=True, validate=validate.Range(1, 4))
    grading_speed = fields.Int(required=True, validate=validate.Range(1, 4))
    resourcefulness = fields.Int(required=True, validate=validate.Range(1, 4))

    easiness = fields.Int(required=True, validate=validate.Range(1, 4))
    workload = fields.Int(required=True, validate=validate.Range(1, 4))

    recommended = fields.Int(required=True, validate=validate.Range(1, 4))
    comment = fields.Str(required=True, validate=validate.Length(min=1, max=1000))

    class Meta:
        strict = True


class EvaluationsResource(Resource):

    @auth_required(Permission.WriteEvaluations)
    def get(self):
        ident = get_jwt_identity()
        evals = Evaluation.query.options(
            subqueryload(Evaluation.professor),
            subqueryload(Evaluation.section).subqueryload(Section.course)
        ).filter_by(student_id=ident['id'])

        return [
            {
                **ev.to_dict(),
                'quarter_id': ev.section.quarter_id,
                'professor': ev.professor.to_dict(),
                'course': ev.section.course.to_dict()
            }
            for ev in evals.all()
        ]

    args = {
        'quarter_id': fields.Int(required=True),
        'professor_id': fields.Int(required=True),
        'course_id': fields.Int(required=True),
        'display_grad_year': fields.Bool(required=True),
        'display_majors': fields.Bool(required=True),
        'evaluation': fields.Nested(EvaluationSchemaV1, required=True)
    }

    @auth_required(Permission.WriteEvaluations)
    @use_args(args, locations=('json',))
    def post(self, args):
        section = db.session.query(Section.id).filter(
            Section.quarter_id == args['quarter_id'],
            Section.course_id == args['course_id'],
            Section.professors.any(Professor.id == args['professor_id']),
            Section.quarter.has(Quarter.university_id == current_user.university_id)
        ).one_or_none()

        if section is None:
            raise UnprocessableEntity('invalid quarter/course/professor combination')

        ev = db.session.query(Evaluation.query.filter(
            Evaluation.section.has(quarter_id=args['quarter_id'], course_id=args['course_id']),
            Evaluation.professor_id == args['professor_id'],
            Evaluation.student_id == current_user.id
        ).exists()).scalar()

        if ev:
            raise Conflict('evaluation for this combination already exists')

        evaluation = Evaluation(
            student_id=current_user.id,
            professor_id=args['professor_id'],
            section_id=section[0],
            display_grad_year=args['display_grad_year'],
            display_majors=args['display_majors'],
            version=1,
            data=args['evaluation']
        )

        db.session.add(evaluation)

        # extend their read access until the end of the current quarter
        cur_quarter_period = db.session.query(Quarter.period).filter_by(current=True).one()[0]
        current_user.read_access = datetime_from_date(cur_quarter_period.upper + timedelta(days=1, hours=11),
                                                      tzinfo=timezone.utc)

        db.session.commit()

        return {
                   'result': 'success',
                   'jwt': create_access_token(identity=current_user.to_dict())
               }, 201


class EvaluationsRecentResource(Resource):

    @auth_required(Permission.WriteEvaluations)
    @use_args({'count': fields.Int(missing=10, validate=validate.Range(min=1, max=25))})
    def get(self, args):
        evals = Evaluation.query.options(
            subqueryload(Evaluation.professor),
            subqueryload(Evaluation.section).subqueryload(Section.course)
        ).filter(
            Evaluation.professor.has(Professor.university_id == current_user.university_id)
        ).order_by(Evaluation.post_time.desc()).limit(args['count'])

        return [
            {
                **ev.to_dict(),
                'quarter_id': ev.section.quarter_id,
                'professor': ev.professor.to_dict(),
                'course': ev.section.course.to_dict()
            }
            for ev in evals.all()
        ]


class EvaluationResource(Resource):

    @auth_required(Permission.ReadEvaluations)
    def get(self, e_id):
        evaluation = Evaluation.query.filter(
            Evaluation.id == e_id,
            Evaluation.section.has(Section.quarter.has(Quarter.university_id == current_user.university_id)),
        ).one_or_none()

        if evaluation is None:
            raise NotFound('evaluation with the specified id not found')

        return evaluation.to_dict()

    @auth_required(Permission.WriteEvaluations)
    def delete(self, e_id):
        ident = get_jwt_identity()
        ev = Evaluation.query.get(e_id)

        if ev is None:
            raise NotFound('evaluation with the specified id not found')

        if ev.student_id != ident['id']:
            raise Forbidden('you are only allowed to delete your own evaluations')

        db.session.delete(ev)
        db.session.commit()

        return '', 204


class EvaluationVoteResource(Resource):
    values = {
        'u': Vote.UPVOTE,
        'd': Vote.DOWNVOTE
    }

    @auth_required(Permission.ReadEvaluations)
    @use_args({'value': fields.Str(required=True, validate=validate.OneOf(['u', 'd']))}, locations=('json',))
    def put(self, args, e_id):
        student_id = get_jwt_identity()['id']
        value = self.values[args['value']]

        evaluation = Evaluation.query.filter(
            Evaluation.id == e_id,
            Evaluation.section.has(Section.quarter.has(Quarter.university_id == current_user.university_id))
        ).one_or_none()

        if evaluation is None:
            raise NotFound('evaluation with the specified id not found')

        # do not allow voting on your own evaluations
        if evaluation.student_id == student_id:
            raise Forbidden('not allowed to vote on your own evaluations')

        vote = Vote.query.filter(
            Vote.evaluation == evaluation,
            Vote.student_id == student_id
        ).one_or_none()

        if vote is None:
            db.session.add(Vote(value=value, student_id=student_id, evaluation=evaluation))
            db.session.commit()
            return '', 201
        elif vote.value != value:
            vote.value = value
            vote.time = func.now()
            db.session.commit()

        return '', 204

    @auth_required(Permission.ReadEvaluations)
    def delete(self, e_id):
        evaluation = Evaluation.query.filter(
            Evaluation.id == e_id,
            Evaluation.section.has(Section.quarter.has(Quarter.university_id == current_user.university_id))
        ).one_or_none()

        if evaluation is None:
            raise NotFound('evaluation with the specified id not found')

        vote = Vote.query.filter(
            Vote.evaluation == evaluation,
            Vote.student_id == current_user.id
        ).one_or_none()

        if vote is None:
            raise NotFound('vote not found')

        db.session.delete(vote)
        db.session.commit()

        return '', 204
