from flask import jsonify
from scuevals_api import app


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


class InternalServerError(Error):
    status_code = 500


@app.errorhandler(Error)
@app.errorhandler(BadRequest)
@app.errorhandler(InternalServerError)
def handle_error(error):
    resp = jsonify(error.to_dict())
    resp.status_code = error.status_code
    return resp
