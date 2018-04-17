from flask_jwt_extended import get_jwt_identity, current_user
from flask_restful import Resource
from marshmallow import fields, validate
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import NotFound

from scuevals_api.models import (
    Permission, Professor, Section, Evaluation, Course, EvaluationScores, db
)
from scuevals_api.auth import auth_required
from scuevals_api.utils import use_args


class ProfessorsResource(Resource):

    @auth_required(Permission.ReadEvaluations, Permission.WriteEvaluations)
    @use_args({'course_id': fields.Int(), 'quarter_id': fields.Int()})
    def get(self, args):
        ident = get_jwt_identity()
        professors = Professor.query.filter(
            Professor.university_id == ident['university_id']
        )

        section_filters = []

        if 'course_id' in args:
            section_filters.append(Section.course_id == args['course_id'])

        if 'quarter_id' in args:
            section_filters.append(Section.quarter_id == args['quarter_id'])

        if section_filters:
            expr = True
            for fil in section_filters:
                expr = and_(expr, fil)

            professors = professors.filter(Professor.sections.any(expr))

        return [professor.to_dict() for professor in professors.all()]


class ProfessorsTopResource(Resource):

    @auth_required(Permission.ReadEvaluations, Permission.WriteEvaluations)
    @use_args({'count': fields.Int(validate=validate.Range(1, 50)), 'department_id': fields.List(fields.Int())})
    def get(self, args):
        professors = db.session.query(
            Professor,
            func.avg(EvaluationScores.avg_course).label('avg_professor')
        ).join(Professor.evaluations).join(
            EvaluationScores,
            Evaluation.id == EvaluationScores.evaluation_id
        ).filter(
            Professor.university_id == current_user.university_id,
        ).group_by(Professor).order_by(desc('avg_professor'))

        if 'department_id' in args:
            professors = professors.filter(
                Evaluation.section.has(Section.course.has(Course.department_id.in_(args['department_id'])))
            )

        if 'count' in args:
            professors = professors.limit(args['count'])

        return [
            {
                'professor': result.Professor.to_dict(),
                'avg_score': float(result.avg_professor),
            }
            for result in professors.all()
        ]


class ProfessorResource(Resource):

    @auth_required(Permission.ReadEvaluations)
    @use_args({'embed': fields.Str(validate=validate.OneOf(['courses']))})
    def get(self, args, p_id):
        q = Professor.query.options(
            subqueryload(Professor.evaluations).subqueryload(Evaluation.votes)
        ).filter(
            Professor.id == p_id,
            Professor.university_id == current_user.university_id
        )

        professor = q.one_or_none()

        if professor is None:
            raise NotFound('professor with the specified id not found')

        data = professor.to_dict()
        data['evaluations'] = [
            {
                **ev.to_dict(),
                'user_vote': ev.user_vote(current_user),
                'user_flagged': ev.user_flag(current_user),
                'quarter_id': ev.section.quarter_id,
                'course': ev.section.course.to_dict(),
                'author': {
                    'self': current_user.id == ev.student.id,
                    'majors': ev.student.majors_list if ev.display_majors else None,
                    'graduation_year': ev.student.graduation_year if ev.display_grad_year else None
                }
            }
            for ev in professor.evaluations
        ]

        if 'embed' in args:
            courses = Course.query.filter(
                Course.sections.any(Section.professors.any(Professor.id == p_id))
            ).all()

            data['courses'] = [course.to_dict() for course in courses]

        return data
