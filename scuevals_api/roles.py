from functools import wraps
from flask_jwt_extended import get_jwt_identity
from scuevals_api.errors import Unauthorized


# source: https://stackoverflow.com/a/32292739/998919
def optional_arg_decorator(fn):
    @wraps(fn)
    def wrapped_decorator(*args, **kwargs):
        is_bound_method = hasattr(args[0], fn.__name__) if args else False

        if is_bound_method:
            klass = args[0]
            args = args[1:]
        else:
            klass = None

        # If no arguments were passed...
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            if is_bound_method:
                return fn(klass, args[0])
            else:
                return fn(args[0])

        else:
            def real_decorator(decoratee):
                if is_bound_method:
                    return fn(klass, decoratee, *args, **kwargs)
                else:
                    return fn(decoratee, *args, **kwargs)
            return real_decorator
    return wrapped_decorator


@optional_arg_decorator
def role_required(fn, *roles):
    """
    If you decorate a view with this, it will ensure that the requester has at
    least one of the listed roles in its JWT.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        accepted_roles = set(roles)

        jwt_data = get_jwt_identity()

        if 'roles' not in jwt_data:
            raise Unauthorized('unauthorized')

        if len(accepted_roles.intersection(jwt_data['roles'])) == 0:
            raise Unauthorized('unauthorized')

        return fn(*args, **kwargs)
    return wrapper
