from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.exceptions import Unauthorized


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

        if permission is not None and permission not in identity['permissions']:
            raise Unauthorized('unauthorized')

        return fn(*args, **kwargs)
    return wrapper
