import json
import logging

from flask_jwt_extended import get_jwt_identity, current_user
from flask_restful import Resource
from marshmallow import fields, Schema, validate, EXCLUDE
from sqlalchemy import text, and_, func, desc
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import UnprocessableEntity, NotFound

from scuevals_api.models import (
    Permission, Course, Section, db, Department, School, Professor, Evaluation, EvaluationScores
)
from scuevals_api.auth import auth_required
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
        unknown = EXCLUDE


class CoursesResource(Resource):

    @auth_required(Permission.ReadEvaluations, Permission.WriteEvaluations)
    @use_args({'professor_id': fields.Int(), 'quarter_id': fields.Int()})
    def get(self, args):
        ident = get_jwt_identity()
        courses = Course.query.filter(
            Course.department.has(Department.school.has(School.university_id == ident['university_id']))
        )

        course_filters = []

        if 'professor_id' in args:
            course_filters.append(Section.professors.any(Professor.id == args['professor_id']))

        if 'quarter_id' in args:
            course_filters.append(Section.quarter_id == args['quarter_id'])

        if course_filters:
            expr = True
            for fil in course_filters:
                expr = and_(expr, fil)

            courses = courses.filter(Course.sections.any(expr))

        return [course.to_dict() for course in courses.all()]

    @auth_required(Permission.UpdateCourses)
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

            if e.orig.pgcode == 'MIDEP':
                msg = get_pg_error_msg(e.orig)
                logging.error(msg)
                raise UnprocessableEntity(msg)

            logging.error('failed to update courses: ' + str(e))
            raise UnprocessableEntity()

        return {'result': 'success', 'updated_count': int(result.first()[0])}


class CoursesTopResource(Resource):
    @auth_required(Permission.ReadEvaluations, Permission.WriteEvaluations)
    @use_args({'count': fields.Int(validate=validate.Range(1, 50)), 'department_id': fields.List(fields.Int())})
    def get(self, args):
        courses = db.session.query(
            Course,
            func.avg(EvaluationScores.avg_course).label('avg_course')
        ).filter(
            Course.department.has(Department.school.has(School.university_id == current_user.university_id))
        ).join(Course.sections, Section.evaluations).join(
            EvaluationScores,
            Evaluation.id == EvaluationScores.evaluation_id
        ).group_by(Course).order_by(desc('avg_course'))

        if 'department_id' in args:
            courses = courses.filter(Course.department_id.in_(args['department_id']))

        if 'count' in args:
            courses = courses.limit(args['count'])

        return [
            {
                'course': result.Course.to_dict(),
                'avg_score': float(result.avg_course),
            }
            for result in courses.all()
        ]


class CourseResource(Resource):

    @auth_required(Permission.ReadEvaluations)
    @use_args({'embed': fields.Str(validate=validate.OneOf(['professors']))})
    def get(self, args, c_id):
        q = Course.query.options(
            subqueryload(Course.sections).subqueryload(Section.evaluations)
        ).filter(
            Course.id == c_id,
            Course.department.has(Department.school.has(School.university_id == current_user.university_id))
        )

        course = q.one_or_none()

        if course is None:
            raise NotFound('course with the specified id not found')

        data = course.to_dict()
        data['evaluations'] = [
            {
                **ev.to_dict(),
                'user_vote': ev.user_vote(current_user),
                'user_flagged': ev.user_flag(current_user),
                'quarter_id': ev.section.quarter_id,
                'professor': ev.professor.to_dict(),
                'author': {
                    'self': current_user.id == ev.student.id,
                    'majors': ev.student.majors_list if ev.display_majors else None,
                    'graduation_year': ev.student.graduation_year if ev.display_grad_year else None
                }
            }
            for section in course.sections for ev in section.evaluations
        ]

        if 'embed' in args:
            professors = Professor.query.filter(
                Professor.sections.any(Section.course.has(Course.id == c_id))
            ).all()

            data['professors'] = [professor.to_dict() for professor in professors]

        return data
