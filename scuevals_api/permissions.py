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
def permission_required(fn, permission):
    """
    If you decorate a view with this, it will ensure that the requester has the
    specified permission in its JWT.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()

        if permission not in identity['permissions']:
            raise Unauthorized('unauthorized')

        return fn(*args, **kwargs)
    return wrapper
