import json
import logging
from datetime import datetime
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy import text, func
from sqlalchemy.exc import DatabaseError
from marshmallow import fields, validate, Schema
from flask_restful import Resource, Api
from werkzeug.exceptions import Unauthorized, InternalServerError, UnprocessableEntity

from scuevals_api.roles import role_required
from scuevals_api.models import Course, Quarter, Department, School, Section, Professor, db, Major, Student, Role, \
    Evaluation
from scuevals_api.utils import use_args, get_pg_error_msg

resources_bp = Blueprint('resources', __name__)
api = Api(resources_bp)


class DepartmentSchema(Schema):
    value = fields.Str(required=True)
    label = fields.Str(required=True)
    school = fields.Str(required=True)

    class Meta:
        strict = True


class Departments(Resource):

    @jwt_required
    @role_required(Role.Student, Role.API_Key)
    def get(self):
        jwt_data = get_jwt_identity()

        departments = Department.query.join(Department.school).filter(
            School.university_id == jwt_data['university_id']
        ).all()

        return [
            {
                'id': department.id,
                'abbr': department.abbreviation,
                'name': department.name,
                'school': department.school.abbreviation
            }
            for department in departments
        ]

    @jwt_required
    @role_required(Role.API_Key)
    @use_args({'departments': fields.List(fields.Nested(DepartmentSchema), required=True)}, locations=('json',))
    def post(self, args):
        jwt_data = get_jwt_identity()

        params = {'u_id': jwt_data['university_id'], 'data': json.dumps(args)}

        try:
            sql = text('select update_departments(:u_id, (:data)::jsonb)')
            result = db.session.execute(sql, params)
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            db.session.remove()
            logging.error('failed to update departments: ' + str(e))
            raise UnprocessableEntity()

        return {'result': 'success', 'updated_count': int(result.first()[0])}


class CourseSchema(Schema):
    term = fields.Str(required=True)
    catalog_nbr = fields.Str(required=True)
    subject = fields.Str(required=True)
    class_descr = fields.Str(required=True)
    instr_1 = fields.Str(required=True)
    instr_2 = fields.Str(required=True)
    instr_3 = fields.Str(required=True)

    class Meta:
        strict = True


class Courses(Resource):

    @jwt_required
    @role_required(Role.Student)
    @use_args({'quarter_id': fields.Integer()})
    def get(self, args):

        if 'quarter_id' not in args:
            courses = Course.query.all()
        else:
            courses = Course.query.join(Course.sections).filter(Section.quarter_id == args['quarter_id']).all()

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

    @jwt_required
    @role_required(Role.API_Key)
    @use_args({'courses': fields.List(fields.Nested(CourseSchema), required=True)}, locations=('json',))
    def post(self, args):
        jwt_data = get_jwt_identity()
        params = {'u_id': jwt_data['university_id'], 'data': json.dumps(args)}

        try:
            sql = text('select update_courses(:u_id, (:data)::jsonb)')
            result = db.session.execute(sql, params)
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            db.session.remove()

            if e.orig.pgcode == 'MIDEP':
                msg = get_pg_error_msg(e.orig)
                logging.error(msg)
                raise UnprocessableEntity(msg)

            logging.error('failed to update courses: ' + str(e))
            raise UnprocessableEntity

        return {'result': 'success', 'updated_count': int(result.first()[0])}


class Quarters(Resource):

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


class Majors(Resource):

    @jwt_required
    @role_required(Role.Student, Role.Incomplete)
    def get(self):
        majors = Major.query.all()

        return [
            {
                'id': major.id,
                'name': major.name
            }
            for major in majors
        ]

    @jwt_required
    @role_required(Role.API_Key)
    @use_args({'majors': fields.List(fields.Raw(), required=True)})
    def post(self, args):
        jwt_data = get_jwt_identity()

        for major_name in args['majors']:
            major = Major(university_id=jwt_data['university_id'], name=major_name)
            db.session.add(major)

        try:
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            db.session.remove()
            logging.error('failed to insert majors: ' + str(e))
            return {'error': 'database error'}

        return {'result': 'success'}


def year_in_range(year):
    return datetime.now().year <= year <= datetime.now().year + 10


class Students(Resource):
    args = {
        'graduation_year': fields.Int(required=True, validate=year_in_range),
        'gender': fields.Str(required=True, validate=validate.OneOf(['m', 'f', 'o'])),
        'majors': fields.List(fields.Int(), required=True, validate=validate.Length(1, 3)),
    }

    @jwt_required
    @role_required(Role.Student, Role.Incomplete)
    @use_args(args, locations=('json',))
    def patch(self, args, s_id):
        user = get_jwt_identity()
        if user['id'] != s_id:
            raise Unauthorized('you do not have the rights to modify another student')

        student = Student.query.get(s_id)
        if student is None:
            raise InternalServerError('user does not exist')

        student.graduation_year = args['graduation_year']
        student.gender = args['gender']

        try:
            student.majors_list = args['majors']
        except ValueError:
            raise UnprocessableEntity('invalid major(s) specified')

        inc = Role.query.get(Role.Incomplete)
        if inc in student.roles:
            student.roles.remove(inc)
            student.roles.append(Role.query.get(Role.Student))

        db.session.commit()

        ident = student.to_dict()

        return {
            'result': 'success',
            'jwt': create_access_token(identity=ident)
        }


class EvaluationSchemaV1(Schema):
    attitude = fields.Int(required=True, validate=validate.Range(1, 4))
    availability = fields.Int(required=True, validate=validate.Range(1, 4))
    clarity = fields.Int(required=True, validate=validate.Range(1, 4))
    handwriting = fields.Int(required=True, validate=validate.Range(1, 4))
    take_again = fields.Int(required=True, validate=validate.Range(1, 4))
    timeliness = fields.Int(required=True, validate=validate.Range(1, 4))

    evenness = fields.Int(required=True, validate=validate.Range(1, 4))
    workload = fields.Int(required=True, validate=validate.Range(1, 4))

    comment = fields.Str(required=True, validate=validate.Length(min=1, max=750))

    class Meta:
        strict = True


class Evaluations(Resource):
    args = {
        'quarter_id': fields.Int(required=True),
        'professor_id': fields.Int(required=True),
        'course_id': fields.Int(required=True),
        'evaluation': fields.Nested(EvaluationSchemaV1)
    }

    @jwt_required
    @role_required(Role.Student)
    @use_args(args, locations=('json',))
    def post(self, args):
        section = Section.query.filter(
            Section.quarter_id == args['quarter_id'],
            Section.course_id == args['course_id']
        ).one_or_none()

        if section is None:
            raise UnprocessableEntity('invalid quarter/course combination')

        ident = get_jwt_identity()

        evaluation = Evaluation(
            student_id=ident['id'],
            professor_id=args['professor_id'],
            section_id=section.id,
            version=1,
            data=args['evaluation']
        )

        db.session.add(evaluation)
        db.session.commit()

        return {'result': 'success'}, 201


api.add_resource(Departments, '/departments')
api.add_resource(Courses, '/courses')
api.add_resource(Quarters, '/quarters')
api.add_resource(Majors, '/majors')
api.add_resource(Search, '/search')
api.add_resource(Students, '/students/<int:s_id>')
api.add_resource(Evaluations, '/evaluations')
