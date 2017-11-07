from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy import func

from scuevals_api.models import Role, Course, Department, School, Professor
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args


class Search(Resource):
    args = {'q': fields.String(required=True), 'limit': fields.Integer()}

    @jwt_required
    @role_required(Role.Student)
    @use_args(args)
    def get(self, args):
        jwt_data = get_jwt_identity()

        if 'limit' not in args or args['limit'] > 50:
            args['limit'] = 50

        # strip any characters that would cause matching issues
        q = args['q'].replace(',', '')

        courses = Course.query.join(Course.department, Department.school).filter(
            School.university_id == jwt_data['university_id']
        ).filter(
            func.concat(Department.abbreviation, ' ', Course.number, ' ', Course.title).ilike('%{}%'.format(q))
        ).limit(args['limit']).all()

        professors = Professor.query.filter(
            func.concat(Professor.last_name, ' ', Professor.first_name).ilike('%{}%'.format(q)) |
            func.concat(Professor.first_name, ' ', Professor.last_name).ilike('%{}%'.format(q))
        ).limit(args['limit']).all()

        return {
            'courses': [
                {
                    'id': course.id,
                    'department': course.department.abbreviation,
                    'number': course.number,
                    'title': course.title,
                    'quarters': [section.quarter.id for section in course.sections]
                }
                for course in courses
            ],
            'professors': [
                {
                    'id': professor.id,
                    'first_name': professor.first_name,
                    'last_name': professor.last_name
                }
                for professor in professors
            ]
        }
