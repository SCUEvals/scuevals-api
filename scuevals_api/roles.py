from functools import wraps
from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import Unauthorized


# source: https://stackoverflow.com/a/26151604/998919
def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer


@parametrized
def role_required(fn, *roles):
    """
    If you decorate a view with this, it will ensure that the requester has at
    least one of the listed roles in its JWT.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        accepted_roles = set(roles)

        jwt_data = get_jwt_identity()

        if 'roles' not in jwt_data or len(accepted_roles.intersection(jwt_data['roles'])) == 0:
            raise Unauthorized('unauthorized')

        return fn(*args, **kwargs)
    return wrapper
