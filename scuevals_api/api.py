import json
import logging
import os
import requests
import time
from flask import request
from flask_jwt_simple import jwt_required, create_jwt
from sqlalchemy import text, func
from sqlalchemy.exc import DatabaseError
from webargs import fields, missing
from webargs.flaskparser import parser, use_kwargs
from scuevals_api.exceptions import BadRequest
from scuevals_api.models import Course, Quarter, Department, School, Section, Professor
from scuevals_api import api, db, app
from flask_restful import Resource, abort


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


@app.route('/auth', methods=['POST'])
@use_kwargs({'id_token': fields.String()})
def auth(id_token):
    if request.headers['Content-Type'] != 'application/json':
        raise BadRequest('wrong mime type')

    resp = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo', params={id_token: id_token})

    if resp.status_code != 200:
        raise BadRequest('failed to validate id_token with Google')

    data = resp.json()
    if data['iss'] not in ('https://accounts.google.com', 'accounts.google.com'):
        raise BadRequest('invalid id_token')

    if data['aud'] != os.environ['GOOGLE_CLIENT_ID']:
        raise BadRequest('invalid id_token')

    if data['exp'] < time.time():
        raise BadRequest('inavlid id_token')

    # TODO: Get this value from the database
    if data['hd'] != 'scu.edu':
        raise BadRequest('inavlid id_token')

    return {'jwt': create_jwt(identity=data['email'])}


api.add_resource(Departments, '/departments')
api.add_resource(Courses, '/courses')
api.add_resource(Quarters, '/quarters')
api.add_resource(Search, '/search')
