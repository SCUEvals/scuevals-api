from flask import Blueprint, jsonify


errors_bp = Blueprint('errors', __name__)


class Error(Exception):
    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'error': self.message}


class BadRequest(Error):
    status_code = 400


class Unauthorized(Error):
    status_code = 401


class UnprocessableEntity(Error):
    status_code = 422


class InternalServerError(Error):
    status_code = 500


@errors_bp.app_errorhandler(Error)
@errors_bp.app_errorhandler(BadRequest)
@errors_bp.app_errorhandler(InternalServerError)
@errors_bp.app_errorhandler(Unauthorized)
def handle_error(error):
    resp = jsonify(error.to_dict())
    resp.status_code = error.status_code
    return resp
