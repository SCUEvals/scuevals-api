import os
import rollbar
import rollbar.contrib.flask
from flask import Blueprint, jsonify, got_request_exception


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


@errors_bp.before_app_first_request
def init_rollbar():
    """init rollbar module"""

    if 'ROLLBAR_API_KEY' not in os.environ or 'FLASK_CONFIG' not in os.environ:
        return

    rollbar.init(
        # access token
        os.environ['ROLLBAR_API_KEY'],
        # environment name
        os.environ['FLASK_CONFIG'],
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, errors_bp)
