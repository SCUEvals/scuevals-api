from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy import func

from scuevals_api.models import Permission, Course, Department, School, Professor
from scuevals_api.auth import auth_required
from scuevals_api.utils import use_args


class SearchResource(Resource):
    args = {'q': fields.String(required=True), 'limit': fields.Integer()}

    @auth_required(Permission.ReadEvaluations)
    @use_args(args)
    def get(self, args):
        jwt_data = get_jwt_identity()

        if 'limit' not in args or args['limit'] > 50:
            args['limit'] = 50

        # strip any characters that would cause matching issues
        q = args['q'].replace(',', '')

        courses = Course.query.join(Course.department).filter(
            Course.department.has(Department.school.has(School.university_id == jwt_data['university_id']))
        ).filter(
            func.concat(Department.abbreviation, ' ', Course.number, ' ', Course.title).ilike('%{}%'.format(q))
        ).limit(args['limit'])

        professors = Professor.query.filter(
            func.concat(Professor.last_name, ' ', Professor.first_name).ilike('%{}%'.format(q)) |
            func.concat(Professor.first_name, ' ', Professor.last_name).ilike('%{}%'.format(q))
        ).limit(args['limit'])

        return {
            'courses': [
                course.to_dict() for course in courses.all()
            ],
            'professors': [
                professor.to_dict() for professor in professors.all()
            ]
        }
