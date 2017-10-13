import json
import logging
from datetime import datetime
from flask import Blueprint, request
from flask_jwt_simple import jwt_required, get_jwt_identity
from sqlalchemy import text, func
from sqlalchemy.exc import DatabaseError
from webargs import missing, fields
from webargs.flaskparser import parser, use_kwargs
from scuevals_api.errors import BadRequest, Unauthorized, InternalServerError
from scuevals_api.models import Course, Quarter, Department, School, Section, Professor, db, Major, Student
from flask_restful import Resource, abort, Api

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

        data = request.get_json()
        if 'departments' not in data or not isinstance(data['departments'], list):
            raise BadRequest('invalid json format')

        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        params = {'u_id': university_id, 'data': json.dumps(data)}

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

        data = request.get_json()
        if 'courses' not in data or not isinstance(data['courses'], list):
            raise BadRequest('invalid json format')

        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        params = {'u_id': university_id, 'data': json.dumps(data)}

        try:
            sql = text('select update_courses(:u_id, (:data)::jsonb)')
            result = db.session.execute(sql, params)
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            db.session.remove()
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


class Majors(Resource):
    args = {'university_id': fields.Integer()}

    @use_kwargs(args)
    def get(self, university_id):
        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        majors = Major.query.all()

        return [
            {
                'id': major.id,
                'name': major.name
            }
            for major in majors
        ]

    @use_kwargs(args)
    def post(self, university_id):
        if request.headers['Content-Type'] != 'application/json':
            raise BadRequest('wrong mime type')

        data = request.get_json()
        if 'majors' not in data or not isinstance(data['majors'], list):
            raise BadRequest('invalid json format')

        if university_id is missing:
            raise BadRequest('missing university_id parameter')

        for major_name in data['majors']:
            major = Major(university_id=university_id, name=major_name)
            db.session.add(major)

        try:
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            db.session.remove()
            logging.error('failed to insert majors: ' + str(e))
            return {'error': 'database error'}

        return {'result': 'success'}


class Students(Resource):
    @jwt_required
    def patch(self, s_id):
        user = get_jwt_identity()
        if user['id'] != s_id:
            raise Unauthorized('you do not have the rights to modify another student')

        student = Student.query.get(s_id)
        if student is None:
            raise InternalServerError('user does not exist')

        if request.headers['Content-Type'] != 'application/json':
            raise BadRequest('wrong mime type')

        data = request.get_json()

        if not (datetime.now().year <= data['graduation_year'] <= datetime.now().year + 10):
            raise BadRequest('graduation year out of bounds')

        student.graduation_year = data['graduation_year']

        if not data['gender'] in ('m', 'f', 'o'):
            raise BadRequest('invalid gender')

        student.gender = data['gender']

        if not (0 < len(data['majors']) <= 3):
            raise BadRequest('number of majors out of bounds')

        try:
            student.majors_list = data['majors']
        except ValueError:
            raise BadRequest('invalid major(s) specified')

        return {'result': 'success'}


@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)


api.add_resource(Departments, '/departments')
api.add_resource(Courses, '/courses')
api.add_resource(Quarters, '/quarters')
api.add_resource(Majors, '/majors')
api.add_resource(Search, '/search')
api.add_resource(Students, '/students/<int:s_id>')
