from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from flask_restful import Resource
from marshmallow import fields, validate
from sqlalchemy import and_
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import NotFound

from scuevals_api.models import Permission, Professor, Section, Evaluation
from scuevals_api.permissions import permission_required
from scuevals_api.utils import use_args


class ProfessorsResource(Resource):

    @jwt_required
    @permission_required(Permission.Write)
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


class ProfessorResource(Resource):

    @jwt_required
    @permission_required(Permission.Read)
    @use_args({'embed': fields.Str(validate=validate.OneOf(['courses']))})
    def get(self, args, p_id):
        q = Professor.query.options(
            subqueryload(Professor.evaluations).subqueryload(Evaluation.votes)
        ).filter(
            Professor.id == p_id,
            Professor.university_id == current_user.university_id
        )

        if 'embed' in args:
            q.options(subqueryload(Professor.sections).subqueryload(Section.course))

        professor = q.one_or_none()

        if professor is None:
            raise NotFound('professor with the specified id not found')

        data = professor.to_dict()
        data['evaluations'] = [
            {
                **ev.to_dict(),
                'user_vote': ev.user_vote(current_user),
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
            data['courses'] = [section.course.to_dict() for section in professor.sections]

        return data
