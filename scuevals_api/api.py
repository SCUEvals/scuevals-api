import json
from flask import request
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from webargs import fields, missing
from webargs.flaskparser import parser, use_kwargs
from scuevals_api.models import Course, Quarter, Department, School
from scuevals_api import api, db
from flask_restful import Resource, abort


class Departments(Resource):
    args = {'university_id': fields.Integer()}

    @use_kwargs(args)
    def get(self, university_id):
        if university_id is missing:
            return {'error': 'missing university_id parameter'}

        departments = Department.query.join(Department.school).filter(School.university_id == university_id).all()

        return [
            {
                'id': department.id,
                'abbr': department.abbreviation,
                'school': department.school.abbreviation
            }
            for department in departments
        ]

    @use_kwargs(args)
    def post(self, university_id):
        if request.headers['Content-Type'] != 'application/json':
            return {'error': 'wrong mime type'}

        if 'departments' not in request.json or not isinstance(request.json['departments'], list):
            return {'error': 'invalid json format'}

        params = {'u_id': university_id, 'data': json.dumps(request.json)}

        try:
            result = db.engine.execute(text('select update_departments(:u_id, (:data)::jsonb)'), params)
        except DatabaseError:
            return {'error': 'invalid json format'}

        return {'result': 'success', 'updated_count': int(result.first()[0])}


class Courses(Resource):
    args = {'quarter_id': fields.Integer()}

    @use_kwargs(args)
    def get(self, quarter_id):

        if quarter_id is missing:
            courses = Course.query.all()
        else:
            courses = Course.query.join(Course.quarters).filter(Quarter.id == quarter_id).all()

        return [
            {
                'id': course.id,
                'department': course.department.abbreviation,
                'number': course.number,
                'title': course.title,
                'quarters': [quarter.id for quarter in course.quarters]
            }
            for course in courses
        ]


class Quarters(Resource):
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


@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)


api.add_resource(Departments, '/departments')
api.add_resource(Courses, '/courses')
api.add_resource(Quarters, '/quarters')
