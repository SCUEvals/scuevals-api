import logging

from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import UnprocessableEntity

from scuevals_api.models import Permission, Major, db
from scuevals_api.auth import auth_required
from scuevals_api.utils import use_args


class MajorsResource(Resource):

    @auth_required
    def get(self):
        majors = Major.query.all()

        return [major.to_dict() for major in majors]

    @auth_required(Permission.UpdateMajors)
    @use_args({'majors': fields.List(fields.Str(), required=True)}, locations=('json',))
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
            raise UnprocessableEntity()

        return {'result': 'success'}
