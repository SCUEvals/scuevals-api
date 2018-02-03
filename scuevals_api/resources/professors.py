from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy import and_
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import NotFound

from scuevals_api.auth import validate_university_id
from scuevals_api.models import Role, Professor, Section, Evaluation, Student
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args


class ProfessorsResource(Resource):

    @jwt_required
    @role_required(Role.Student)
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
    @role_required(Role.Student)
    def get(self, p_id):
        professor = Professor.query.options(
            subqueryload(Professor.evaluations).subqueryload(Evaluation.votes)
        ).get(p_id)

        if professor is None:
            raise NotFound('professor with the specified id not found')

        validate_university_id(professor.university_id)

        user = get_jwt_identity()
        student = Student.query.get(user['id'])

        data = professor.to_dict()
        data['evaluations'] = [
            {
                **ev.to_dict(),
                'user_vote': ev.user_vote(student),
                'quarter_id': ev.section.quarter_id,
                'course': ev.section.course.to_dict(),
                'author': {
                    'self': student.id == ev.student.id,
                    'majors': ev.student.majors_list if ev.display_majors else None,
                    'graduation_year': ev.student.graduation_year if ev.display_grad_year else None
                }
            }
            for ev in professor.evaluations
        ]

        return data
