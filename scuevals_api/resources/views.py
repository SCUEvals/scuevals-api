import json
import logging
from flask import Blueprint, request
from flask_jwt_simple import jwt_required
from sqlalchemy import text, func
from sqlalchemy.exc import DatabaseError
from webargs import missing
from webargs.flaskparser import parser, use_kwargs
from scuevals_api.errors import BadRequest
from scuevals_api.models import Course, Quarter, Department, School, Section, Professor, db
from flask_restful import Resource, abort, Api, fields

resources_bp = Blueprint('resources', __name__)
api = Api(resources_bp)


class Departments(Resource):
    args = {'university_id': fields.Integer()}

    @use_kwargs(args)
    def get(self, university_id):
        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        departments = Department.query.join(Department.school).filter(School.university_id == university_id).all()

        return [
            {
                'id': department.id,
                'abbr': department.abbreviation,
                'name': department.name,
                'school': department.school.abbreviation
            }
            for department in departments
        ]

    @use_kwargs(args)
    def post(self, university_id):
        if request.headers['Content-Type'] != 'application/json':
            raise BadRequest('wrong mime type')

        if 'departments' not in request.json or not isinstance(request.json['departments'], list):
            raise BadRequest('invalid json format')

        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        params = {'u_id': university_id, 'data': json.dumps(request.json)}

        try:
            sql = text('select update_departments(:u_id, (:data)::jsonb)')
            result = db.session.execute(sql, params)
            db.session.commit()
        except DatabaseError as e:
            logging.error('failed to update departments: ' + str(e))
            return {'error': 'database error'}

        return {'result': 'success', 'updated_count': int(result.first()[0])}


class Courses(Resource):
    args = {'university_id': fields.Integer(), 'quarter_id': fields.Integer()}

    @use_kwargs(args)
    def get(self, university_id, quarter_id):

        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        if quarter_id is missing:
            courses = Course.query.all()
        else:
            courses = Course.query.join(Course.sections).filter(Section.quarter_id == quarter_id).all()

        return [
            {
                'id': course.id,
                'department': course.department.abbreviation,
                'number': course.number,
                'title': course.title,
                'quarters': [section.quarter.id for section in course.sections]
            }
            for course in courses
        ]

    @use_kwargs(args)
    def post(self, university_id):
        if request.headers['Content-Type'] != 'application/json':
            raise BadRequest('wrong mime type')

        if 'courses' not in request.json or not isinstance(request.json['courses'], list):
            raise BadRequest('invalid json format')

        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        params = {'u_id': university_id, 'data': json.dumps(request.json)}

        try:
            sql = text('select update_courses(:u_id, (:data)::jsonb)')
            result = db.session.execute(sql, params)
            db.session.commit()
        except DatabaseError as e:
            logging.error('failed to update courses: ' + str(e))
            return {'error': 'database error'}

        return {'result': 'success', 'updated_count': int(result.first()[0])}


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


class Search(Resource):
    args = {'university_id': fields.Integer(), 'q': fields.String(), 'limit': fields.Integer()}

    @jwt_required
    @use_kwargs(args)
    def get(self, university_id, q, limit):
        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        if q is missing:
            raise BadRequest('missing q parameter')

        if limit is missing or limit > 50:
            limit = 50

        # strip any characters that would cause matching issues
        q = q.replace(',', '')

        courses = Course.query.join(Course.department).filter(
            func.concat(Department.abbreviation, ' ', Course.number, ' ', Course.title).ilike('%{}%'.format(q))
        ).limit(limit).all()

        professors = Professor.query.filter(
            func.concat(Professor.last_name, ' ', Professor.first_name).ilike('%{}%'.format(q)) |
            func.concat(Professor.first_name, ' ', Professor.last_name).ilike('%{}%'.format(q))
        ).limit(limit).all()

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


@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)


api.add_resource(Departments, '/departments')
api.add_resource(Courses, '/courses')
api.add_resource(Quarters, '/quarters')
api.add_resource(Search, '/search')
