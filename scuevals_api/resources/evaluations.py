from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from flask_restful import Resource
from marshmallow import fields, Schema, validate
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import UnprocessableEntity, NotFound, Forbidden, Conflict

from scuevals_api.models import Vote
from scuevals_api.auth import validate_university_id
from scuevals_api.models import Role, Section, Evaluation, db, Professor, Quarter
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args


class EvaluationSchemaV1(Schema):
    attitude = fields.Int(required=True, validate=validate.Range(1, 4))
    availability = fields.Int(required=True, validate=validate.Range(1, 4))
    clarity = fields.Int(required=True, validate=validate.Range(1, 4))
    grading_speed = fields.Int(required=True, validate=validate.Range(1, 4))
    resourcefulness = fields.Int(required=True, validate=validate.Range(1, 4))

    easiness = fields.Int(required=True, validate=validate.Range(1, 4))
    workload = fields.Int(required=True, validate=validate.Range(1, 4))

    recommended = fields.Int(required=True, validate=validate.Range(1, 4))
    comment = fields.Str(required=True, validate=validate.Length(min=1, max=750))

    class Meta:
        strict = True


class EvaluationsResource(Resource):

    @jwt_required
    @role_required(Role.Student)
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

    @jwt_required
    @role_required(Role.Student)
    @use_args(args, locations=('json',))
    def post(self, args):
        section = db.session.query(Section.id).filter(
            Section.quarter_id == args['quarter_id'],
            Section.course_id == args['course_id'],
            Section.professors.any(Professor.id == args['professor_id'])
        ).one_or_none()

        if section is None:
            raise UnprocessableEntity('invalid quarter/course/professor combination')

        ev = db.session.query(Evaluation.query.filter(
            Evaluation.section.has(quarter_id=args['quarter_id'], course_id=args['course_id']),
            Evaluation.professor_id == args['professor_id']
        ).exists()).scalar()

        if ev:
            raise Conflict('evaluation for this combination already exists')

        ident = get_jwt_identity()

        evaluation = Evaluation(
            student_id=ident['id'],
            professor_id=args['professor_id'],
            section_id=section[0],
            display_grad_year=args['display_grad_year'],
            display_majors=args['display_majors'],
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

    @jwt_required
    @role_required(Role.Student)
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
            db.session.commit()

        return '', 204

    @jwt_required
    @role_required(Role.Student)
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
