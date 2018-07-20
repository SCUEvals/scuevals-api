from flask_jwt_extended import current_user
from flask_restful import Resource
from marshmallow import fields, Schema

from scuevals_api.auth import auth_required
from scuevals_api.models import Permission, OfficialUserType, db
from scuevals_api.utils import use_args


class OfficialUserTypeSchema(Schema):
    email = fields.Str(required=True)
    type = fields.Str(required=True)

    class Meta:
        strict = True


class OfficialUserTypeResource(Resource):
    @auth_required(Permission.UpdateOfficialUserTypes)
    @use_args({'official_user_types': fields.List(fields.Nested(OfficialUserTypeSchema), required=True)},
              locations=('json',))
    def post(self, args):

        for out in args['official_user_types']:
            db.session.merge(OfficialUserType(
                email=out['email'].lower(),
                type=out['type'],
                university_id=current_user.university_id
            ))

        db.session.commit()
        return {'result': 'success', 'updated_count': len(args['official_user_types'])}, 200
