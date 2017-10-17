from functools import wraps
from flask import current_app
from flask_jwt_simple import get_jwt_identity
from scuevals_api.errors import Unauthorized


def role_required(*roles):
    """
    If you decorate a view with this, it will ensure that the requester has at
    least one of the listed roles in its JWT. A ROLE_DEFAULT option can be
    specified in the app config so that this decorator can be used without
    any arguments.
    """
    def role_required_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if len(roles) > 0:
                accepted_roles = set(roles)
                if 'DEFAULT_ROLE' in current_app.config:
                    accepted_roles.add(current_app.config['DEFAULT_ROLE'])

                jwt_data = get_jwt_identity()

                if 'roles' not in jwt_data:
                    raise Unauthorized('unauthorized')

                if len(accepted_roles.intersection(jwt_data['roles'])) == 0:
                    raise Unauthorized('unauthorized')

            return fn(*args, **kwargs)
        return wrapper
    return role_required_decorator
