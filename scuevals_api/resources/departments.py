import json
import logging

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import fields, Schema
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import UnprocessableEntity

from scuevals_api.models import Role, Department, School, db
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args


class DepartmentSchema(Schema):
    value = fields.Str(required=True)
    label = fields.Str(required=True)
    school = fields.Str(required=True)

    class Meta:
        strict = True


class DepartmentsResource(Resource):

    @jwt_required
    @role_required(Role.Student, Role.API_Key)
    def get(self):
        jwt_data = get_jwt_identity()

        departments = Department.query.join(Department.school).filter(
            School.university_id == jwt_data['university_id']
        ).all()

        return [department.to_dict() for department in departments]

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
