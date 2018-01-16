from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import fields
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
        professors = Professor.query.outerjoin(Section, Professor.sections).filter(
            Professor.university_id == ident['university_id']
        )

        for arg, value in args.items():
            d = {arg: value}
            professors = professors.filter_by(**d)

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
            }
            for ev in professor.evaluations
        ]

        return data
