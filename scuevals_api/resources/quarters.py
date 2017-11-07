from flask_jwt_extended import jwt_required
from flask_restful import Resource

from scuevals_api.models import Role, Quarter
from scuevals_api.roles import role_required


class QuartersResource(Resource):

    @jwt_required
    @role_required(Role.Student)
    def get(self):
        quarters = Quarter.query.all()

        return [
            {
                'id': quarter.id,
                'year': quarter.year,
                'name': quarter.name,
                'current': quarter.current
            }
            for quarter in quarters
        ]
