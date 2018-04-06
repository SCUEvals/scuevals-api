from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user
from werkzeug.exceptions import Unauthorized

from scuevals_api.models import User


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
def auth_required(fn, *permissions):
    """
    Decorating a view with this ensures that the requester provided a JWT
    and that the requester has any of the permissions needed to access the view.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        jwt_required(lambda: None)()

        identity = get_jwt_identity()

        if identity['type'] == User.Normal:
            # fail if the user is still suspended
            if current_user.suspended():
                raise Unauthorized('user is suspended')

        if identity['type'] == User.Student:
            # make sure the read access is synced up
            current_user.check_read_access()

        # verify that the user has the correct permissions for this view
        if permissions and len(set(permissions).intersection(current_user.permissions_list)) == 0:
            raise Unauthorized()

        return fn(*args, **kwargs)
    return wrapper
