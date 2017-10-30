from functools import wraps
from flask import jsonify
from flask_rollbar import Rollbar
from werkzeug.exceptions import (
    BadRequest, Unauthorized, Forbidden, NotFound,
    UnprocessableEntity, MethodNotAllowed, UnsupportedMediaType
)

rollbar = Rollbar(ignore_exc=[BadRequest, Unauthorized, Forbidden, NotFound, UnprocessableEntity,
                              MethodNotAllowed, UnsupportedMediaType])


def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON."""
    handle_http_exception = app.handle_http_exception

    @wraps(handle_http_exception)
    def ret_val(exception):
        exc = handle_http_exception(exception)
        return jsonify({'code': exc.code, 'message': exc.description}), exc.code

    return ret_val
