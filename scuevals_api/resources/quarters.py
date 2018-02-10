from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy import and_

from scuevals_api.models import Role, Quarter, Section, Professor
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args


class QuartersResource(Resource):

    @jwt_required
    @role_required(Role.Student)
    @use_args({'course_id': fields.Int(), 'professor_id': fields.Int()})
    def get(self, args):
        ident = get_jwt_identity()
        quarters = Quarter.query.filter(Quarter.university_id == ident['university_id'])

        quarter_filters = []

        if 'course_id' in args:
            quarter_filters.append(Section.course_id == args['course_id'])

        if 'professor_id' in args:
            quarter_filters.append(Section.professors.any(Professor.id == args['professor_id']))

        if quarter_filters:
            expr = True
            for fil in quarter_filters:
                expr = and_(expr, fil)

            quarters = quarters.filter(Quarter.sections.any(expr))

        return [quarter.to_dict() for quarter in quarters.all()]
