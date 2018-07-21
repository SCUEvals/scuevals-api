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


@jwtm.user_loader_callback_loader
def user_loader(identity):
    if identity['type'] == API_KEY_TYPE:
        return APIKey.query.get(identity['id'])

    return User.query.options(
        subqueryload(User.permissions)
    ).with_polymorphic(Student).filter(User.id == identity['id']).one_or_none()
