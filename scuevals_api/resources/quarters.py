from flask_jwt_extended import current_user
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy import and_, func

from scuevals_api.models import Permission, Quarter, Section, Professor
from scuevals_api.auth import auth_required
from scuevals_api.utils import use_args


class QuartersResource(Resource):

    @auth_required(Permission.ReadEvaluations, Permission.WriteEvaluations)
    @use_args({'course_id': fields.Int(), 'professor_id': fields.Int()})
    def get(self, args):
        quarters = Quarter.query.filter(
            func.upper(Quarter.period) <= Quarter.current().with_entities(func.lower(Quarter.period)),
            Quarter.university_id == current_user.university_id
        )

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
