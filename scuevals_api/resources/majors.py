import logging

from flask_jwt_extended import current_user
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy import or_
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import UnprocessableEntity

from scuevals_api.models import Permission, Major, db, Department, School
from scuevals_api.auth import auth_required
from scuevals_api.utils import use_args


class MajorsResource(Resource):

    @auth_required
    def get(self):
        majors = db.session.query(Major).options(
            joinedload(Major.departments)
        ).outerjoin(Major.departments).filter(
            or_(Department.id == None, Department.school.has(School.university_id == current_user.university_id))  # noqa
        )

        return [major.to_dict() for major in majors.all()]

    @auth_required(Permission.UpdateMajors)
    @use_args({'majors': fields.List(fields.Str(), required=True)}, locations=('json',))
    def post(self, args):

        for major_name in args['majors']:
            major = Major(name=major_name)
            db.session.add(major)

        try:
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            db.session.remove()
            logging.error('failed to insert majors: ' + str(e))
            raise UnprocessableEntity()

        return {'result': 'success'}
