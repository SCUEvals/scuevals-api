from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.orm import subqueryload

from scuevals_api.auth import validate_university_id
from scuevals_api.models import Role, Professor
from scuevals_api.roles import role_required


class ProfessorsResource(Resource):

    @jwt_required
    @role_required(Role.Student)
    def get(self):
        ident = get_jwt_identity()
        professors = Professor.query.filter(Professor.university_id == ident['university_id']).all()

        return [professor.to_dict() for professor in professors]


class ProfessorResource(Resource):

    @jwt_required
    @role_required(Role.Student)
    def get(self, p_id):
        professor = Professor.query.options(subqueryload(Professor.evaluations)).get(p_id)

        validate_university_id(professor.university_id)

        data = professor.to_dict()
        data['evaluations'] = [
            {
                'id': ev.id,
                'quarter_id': ev.section.quarter_id,
                'version': ev.version,
                'data': ev.data,
                'course': ev.section.course.to_dict(),
            }
            for ev in professor.evaluations
        ]

        return data
