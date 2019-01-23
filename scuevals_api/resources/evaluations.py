from datetime import timedelta, timezone

from flask_jwt_extended import get_jwt_identity, current_user, create_access_token
from flask_restful import Resource
from marshmallow import fields, Schema, validate
from sqlalchemy import func
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import UnprocessableEntity, NotFound, Forbidden, Conflict

from scuevals_api.models import Permission, Section, Evaluation, db, Professor, Quarter, Vote, Flag, Reason
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
    get_args = {
        'professor_id': fields.Int(),
        'course_id': fields.Int(),
        'quarter_id': fields.Int(),
        'embed': fields.List(fields.Str(validate=validate.OneOf(['professor', 'course'])), missing=[])
    }

    @auth_required(Permission.ReadEvaluations)
    @use_args(get_args)
    def get(self, args):
        return get_evals_json(args)

    post_args = {
        'quarter_id': fields.Int(required=True),
        'professor_id': fields.Int(required=True),
        'course_id': fields.Int(required=True),
        'display_grad_year': fields.Bool(required=True),
        'display_majors': fields.Bool(required=True),
        'evaluation': fields.Nested(EvaluationSchemaV1, required=True)
    }

    @auth_required(Permission.WriteEvaluations)
    @use_args(post_args, locations=('json',))
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
        cur_quarter_period = Quarter.current().with_entities(Quarter.period).one()[0]
        current_user.read_access = datetime_from_date(cur_quarter_period.upper + timedelta(days=1, hours=11),
                                                      tzinfo=timezone.utc)

        db.session.commit()

        return {
                   'result': 'success',
                   'jwt': create_access_token(identity=current_user.to_dict())
               }, 201


class EvaluationsRecentResource(Resource):

    @auth_required(Permission.ReadEvaluations)
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
        evaluation = get_eval(e_id)
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

        evaluation = get_eval(e_id)

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
            return '', 204
        elif vote.value != value:
            vote.value = value
            vote.time = func.now()
            db.session.commit()

        return '', 204

    @auth_required(Permission.ReadEvaluations)
    def delete(self, e_id):
        evaluation = get_eval(e_id)

        vote = Vote.query.filter(
            Vote.evaluation == evaluation,
            Vote.student_id == current_user.id
        ).one_or_none()

        if vote is None:
            raise NotFound('vote not found')

        db.session.delete(vote)
        db.session.commit()

        return '', 204


class EvaluationFlagResource(Resource):
    args = {
        'reason_ids': fields.List(fields.Int(), required=True, validate=validate.Length(min=1)),
        'comment': fields.Str(required=False, validate=validate.Length(max=500))
    }

    @auth_required(Permission.ReadEvaluations)
    @use_args(args, locations=('json',))
    def post(self, args, e_id):

        evaluation = get_eval(e_id)

        # do not allow flagging your own evaluations
        if evaluation.student_id == current_user.id:
            raise Forbidden('not allowed to flag your own evaluations')

        # check if user already flagged this eval
        existing_flag = Flag.query.filter_by(evaluation_id=e_id, user_id=current_user.id).one_or_none()

        if existing_flag is not None:
            raise Conflict('user already flagged this evaluation')

        # get the reasons
        reasons = []
        for reason_id in args['reason_ids']:
            reason = Reason.query.get(reason_id)
            if reason is None:
                raise UnprocessableEntity('no reason with id {} exists'.format(reason_id))
            reasons.append(reason)

        flag = Flag(
            reasons=reasons,
            user_id=current_user.id,
            accused_student_id=evaluation.student_id,
            evaluation_id=evaluation.id
        )

        if 'comment' in args:
            flag.comment = args['comment']

        db.session.add(flag)
        db.session.commit()

        return '', 201


def get_eval(eval_id):
    evaluation = Evaluation.query.filter(
        Evaluation.id == eval_id,
        Evaluation.section.has(Section.quarter.has(Quarter.university_id == current_user.university_id))
    ).one_or_none()

    if evaluation is None:
        raise NotFound('evaluation with the specified id not found')

    return evaluation


def get_evals_json(args, student_id=None):
    evals = Evaluation.query

    if 'professor' in args['embed']:
        evals = evals.options(subqueryload(Evaluation.professor))

    if 'course' in args['embed']:
        evals = evals.options(subqueryload(Evaluation.section).subqueryload(Section.course))

    if student_id is not None:
        evals = evals.filter_by(student_id=student_id)

    if 'professor_id' in args:
        evals = evals.filter_by(professor_id=args['professor_id'])

    if 'course_id' in args:
        evals = evals.filter(Evaluation.section.has(Section.course_id == args['course_id']))

    if 'quarter_id' in args:
        evals = evals.filter(Evaluation.section.has(Section.quarter_id == args['quarter_id']))

    data = []

    for ev in evals.all():
        ev_data = {
            **ev.to_dict(),
            'quarter_id': ev.section.quarter_id,
            'user_vote': ev.user_vote(current_user),
            'user_flagged': ev.user_flag(current_user),
            'author': {
                'self': current_user.id == ev.student.id,
                'majors': ev.student.majors_list if ev.display_majors else None,
                'graduation_year': ev.student.graduation_year if ev.display_grad_year else None
            }
        }

        if 'professor' in args['embed']:
            ev_data['professor'] = ev.professor.to_dict()

        if 'course' in args['embed']:
            ev_data['course'] = ev.section.course.to_dict()

        data.append(ev_data)

    return data
