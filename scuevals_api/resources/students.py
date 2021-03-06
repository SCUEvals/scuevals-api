from datetime import datetime, timezone, timedelta
from flask_jwt_extended import get_jwt_identity, create_access_token, current_user
from flask_restful import Resource
from marshmallow import fields, validate
from werkzeug.exceptions import UnprocessableEntity, Forbidden

from scuevals_api.auth import auth_required
from scuevals_api.models import Permission, Student, Quarter, db
from scuevals_api.utils import use_args, datetime_from_date
from .evaluations import get_evals_json


def year_in_range(year):
    return datetime.now().year <= year <= datetime.now().year + 10


class StudentsResource(Resource):
    args = {
        'graduation_year': fields.Int(required=True, validate=year_in_range),
        'gender': fields.Str(required=True, validate=validate.OneOf(['m', 'f', 'o'])),
        'majors': fields.List(fields.Int(), required=True, validate=validate.Length(1, 3)),
    }

    @auth_required
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

        inc = Permission.query.get(Permission.Incomplete)
        if inc in student.permissions:
            student.permissions.remove(inc)

            # grant them both reading and writing permissions
            student.permissions.append(Permission.query.get(Permission.ReadEvaluations))
            student.permissions.append(Permission.query.get(Permission.WriteEvaluations))

            # set the reading permission to expire when the current quarter expires
            # essentially they get their first quarter free,
            # which makes sense for new students and transfer students
            cur_quarter_period = Quarter.current().with_entities(Quarter.period).one()[0]
            student.read_access = datetime_from_date(cur_quarter_period.upper + timedelta(days=1, hours=11),
                                                     tzinfo=timezone.utc)

        db.session.commit()

        ident = student.to_dict()

        return {
            'result': 'success',
            'jwt': create_access_token(identity=ident)
        }


class StudentEvaluationsResource(Resource):
    get_args = {
        'professor_id': fields.Int(),
        'course_id': fields.Int(),
        'quarter_id': fields.Int(),
        'embed': fields.List(fields.Str(validate=validate.OneOf(['professor', 'course'])), missing=[])
    }

    @auth_required(Permission.WriteEvaluations)
    @use_args(get_args)
    def get(self, args, s_id):
        if current_user.id != s_id:
            raise Forbidden("you do not have the rights to access this student's evaluations")

        return get_evals_json(args, current_user.id)
