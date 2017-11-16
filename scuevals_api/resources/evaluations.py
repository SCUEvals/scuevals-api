from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import fields, Schema, validate
from werkzeug.exceptions import UnprocessableEntity, NotFound

from scuevals_api.models import Vote
from scuevals_api.auth import validate_university_id
from scuevals_api.models import Role, Section, Evaluation, db
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args


class EvaluationSchemaV1(Schema):
    attitude = fields.Int(required=True, validate=validate.Range(1, 4))
    availability = fields.Int(required=True, validate=validate.Range(1, 4))
    clarity = fields.Int(required=True, validate=validate.Range(1, 4))
    handwriting = fields.Int(required=True, validate=validate.Range(1, 4))
    take_again = fields.Int(required=True, validate=validate.Range(1, 4))
    timeliness = fields.Int(required=True, validate=validate.Range(1, 4))

    evenness = fields.Int(required=True, validate=validate.Range(1, 4))
    workload = fields.Int(required=True, validate=validate.Range(1, 4))

    comment = fields.Str(required=True, validate=validate.Length(min=1, max=750))

    class Meta:
        strict = True


class EvaluationsResource(Resource):
    args = {
        'quarter_id': fields.Int(required=True),
        'professor_id': fields.Int(required=True),
        'course_id': fields.Int(required=True),
        'evaluation': fields.Nested(EvaluationSchemaV1)
    }

    @jwt_required
    @role_required(Role.Student)
    @use_args(args, locations=('json',))
    def post(self, args):
        section = Section.query.filter(
            Section.quarter_id == args['quarter_id'],
            Section.course_id == args['course_id']
        ).one_or_none()

        if section is None:
            raise UnprocessableEntity('invalid quarter/course combination')

        ident = get_jwt_identity()

        evaluation = Evaluation(
            student_id=ident['id'],
            professor_id=args['professor_id'],
            section_id=section.id,
            version=1,
            data=args['evaluation']
        )

        db.session.add(evaluation)
        db.session.commit()

        return {'result': 'success'}, 201


class EvaluationResource(Resource):

    @jwt_required
    @role_required(Role.Student)
    def get(self, e_id):
        evaluation = Evaluation.query.get(e_id)
        if evaluation is None:
            raise NotFound('evaluation with the specified id not found')

        validate_university_id(evaluation.section.course.department.school.university_id)

        return evaluation.to_dict()


class EvaluationVoteResource(Resource):

    values = {
        'u': Vote.UPVOTE,
        'd': Vote.DOWNVOTE
    }

    @jwt_required
    @role_required(Role.Student)
    @use_args({'value': fields.Str(required=True, validate=validate.OneOf(['u', 'd']))}, locations=('json',))
    def put(self, args, e_id):
        student_id = get_jwt_identity()['id']
        value = self.values[args['value']]

        evaluation = Evaluation.query.get(e_id)
        if evaluation is None:
            raise NotFound('evaluation with the specified id not found')

        validate_university_id(evaluation.section.course.department.school.university_id)

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
            db.session.commit()

        return '', 204

    @jwt_required
    @role_required(Role.Student)
    def delete(self, e_id):
        student_id = get_jwt_identity()['id']

        evaluation = Evaluation.query.get(e_id)
        if evaluation is None:
            raise NotFound('evaluation with the specified id not found')

        validate_university_id(evaluation.section.course.department.school.university_id)

        vote = Vote.query.filter(
            Vote.evaluation == evaluation,
            Vote.student_id == student_id
        ).one_or_none()

        if vote is None:
            raise NotFound('vote not found')

        db.session.delete(vote)
        db.session.commit()

        return '', 204
