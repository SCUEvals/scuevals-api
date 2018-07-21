import json
import logging

from flask_jwt_extended import current_user
from flask_restful import Resource
from marshmallow import fields, Schema
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError

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
        params = {'u_id': current_user.university_id, 'json_data': json.dumps(args['official_user_types'])}

        # afaik this should not fail due to input data validation and no table constraints
        sql = text(r"""
        with upsert as (
            insert into official_user_type (email, type, university_id)
            select
              u->>'email' as new_email,
              u->>'type' as new_type,
              :u_id
            from jsonb_array_elements((:json_data)::jsonb) u
            on conflict (email)
            do update set type=excluded.type
            returning *
        )
        select count(1) from upsert;
        """)

        result = db.session.execute(sql, params)
        db.session.commit()

        return {'result': 'success', 'updated_count': int(result.first()[0])}, 200
