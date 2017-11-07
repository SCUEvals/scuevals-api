from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_restful import Resource
from marshmallow import fields, validate
from werkzeug.exceptions import Unauthorized, UnprocessableEntity

from scuevals_api.models import Role, Student, db
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args


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
            raise UnprocessableEntity('user does not exist')

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
