from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user
from werkzeug.exceptions import Unauthorized

from scuevals_api.models import Permission
from scuevals_api.models.api_key import API_KEY_TYPE


def optional_arg_decorator(fn):
    def wrapped_decorator(*args):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])

        else:
            def real_decorator(decoratee):
                return fn(decoratee, *args)

            return real_decorator

    return wrapped_decorator


@optional_arg_decorator
def auth_required(fn, permission=None):
    """
    Decorating a view with this ensures that the requester provided a JWT
    and that the requester has permission to access the view.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        jwt_required(lambda: None)()

        identity = get_jwt_identity()

        # verify that the JWT is up-to-date in case it is not API Key access
        if identity['type'] != API_KEY_TYPE:
            # fail if the user is still suspended
            if current_user.suspended():
                raise Unauthorized('invalid or expired user info')

            # fail if the JWT doesn't reflect that the user lost reading access
            if Permission.ReadEvaluations in identity['permissions'] and not current_user.has_reading_access():
                raise Unauthorized('invalid or expired user info')

            # verify that the user has the correct permissions for this view
            if permission is not None and permission not in identity['permissions']:
                raise Unauthorized()

        return fn(*args, **kwargs)
    return wrapper
