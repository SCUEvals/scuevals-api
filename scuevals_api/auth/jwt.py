from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm import subqueryload

from scuevals_api.models import User, Student, APIKey
from scuevals_api.models.api_key import API_KEY_TYPE
from . import jwtm


@jwtm.claims_verification_loader
def claims_verification_loader(user_claims):
    identity = get_jwt_identity()

    keys = [
        'type',
        'permissions',
        'university_id'
    ]

    for key in keys:
        if key not in identity:
            return False

    return True


@jwtm.claims_verification_failed_loader
def claim_verification_failed():
    return jsonify({'message': 'invalid or expired user info'}), 401


@jwtm.user_loader_callback_loader
def user_loader(identity):
    if identity['type'] == API_KEY_TYPE:
        return APIKey.query.get(identity['id'])

    return User.query.options(
        subqueryload(User.permissions)
    ).with_polymorphic(Student).filter(User.id == identity['id']).one_or_none()


@jwtm.user_loader_error_loader
def user_loader_error(identity):
    return jsonify({'message': 'unable to load user'}), 500
