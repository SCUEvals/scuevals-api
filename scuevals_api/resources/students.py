from datetime import datetime, timedelta, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_restful import Resource
from marshmallow import fields, validate
from werkzeug.exceptions import UnprocessableEntity, Forbidden

from scuevals_api.models import Role, Student, db, Quarter
from scuevals_api.roles import role_required
from scuevals_api.utils import use_args, datetime_from_date


def year_in_range(year):
    return datetime.now().year <= year <= datetime.now().year + 10


class StudentsResource(Resource):
    args = {
        'graduation_year': fields.Int(required=True, validate=year_in_range),
        'gender': fields.Str(required=True, validate=validate.OneOf(['m', 'f', 'o'])),
        'majors': fields.List(fields.Int(), required=True, validate=validate.Length(1, 3)),
    }

    @jwt_required
    @role_required(Role.StudentWrite, Role.Incomplete)
    @use_args(args, locations=('json',))
    def patch(self, args, s_id):
        user = get_jwt_identity()
        if user['id'] != s_id:
            raise Forbidden('you do not have the rights to modify another student')

        student = Student.query.get(s_id)

        student.graduation_year = args['graduation_year']
        student.gender = args['gender']

        try:
            student.majors_list = args['majors']
        except ValueError:
            raise UnprocessableEntity('invalid major(s) specified')

        inc = Role.query.get(Role.Incomplete)
        if inc in student.roles:
            student.roles.remove(inc)

            # grant them both reading and writing roles
            # TEMP: only grant them writing role
            # student.roles.append(Role.query.get(Role.StudentRead))
            student.roles.append(Role.query.get(Role.StudentWrite))

            # set the reading role to expire when the current quarter expires
            # cur_quarter_period = db.session.query(Quarter.period).filter_by(current=True).one()[0]
            # student.read_access_until = datetime_from_date(cur_quarter_period.upper + timedelta(days=1),
            #                                                tzinfo=timezone.utc)

        db.session.commit()

        ident = student.to_dict()

        return {
            'result': 'success',
            'jwt': create_access_token(identity=ident)
        }
