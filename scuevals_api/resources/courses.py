import json
import logging

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import fields, Schema
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import UnprocessableEntity, NotFound

from scuevals_api.auth import validate_university_id
from scuevals_api.models import Role, Course, Section, db
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args, get_pg_error_msg


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


class CoursesResource(Resource):

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
            raise UnprocessableEntity()

        return {'result': 'success', 'updated_count': int(result.first()[0])}


class CourseResource(Resource):

    @jwt_required
    @role_required(Role.Student)
    def get(self, c_id):
        course = Course.query.options(
            subqueryload(Course.sections).subqueryload(Section.evaluations)
        ).get(c_id)

        if course is None:
            raise NotFound('course with the specified id not found')

        validate_university_id(course.department.school.university_id)

        data = course.to_dict()
        data['evaluations'] = [
            {
                'id': ev.id,
                'quarter_id': ev.section.quarter_id,
                'version': ev.version,
                'data': ev.data,
                'professor': ev.professor.to_dict(),
            }
            for section in course.sections for ev in section.evaluations
        ]

        return data
