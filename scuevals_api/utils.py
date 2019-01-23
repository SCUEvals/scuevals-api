from datetime import datetime, time

from webargs.flaskparser import FlaskParser, is_json_request
from flask_restful import abort


class StrictRESTParser(FlaskParser):
    DEFAULT_LOCATIONS = ('querystring', 'form',)

    def _parse_request(self, schema, req, locations):
        # return error response if request is not JSON
        if 'json' in locations and not is_json_request(req):
            abort(415)
        return super()._parse_request(schema, req, locations)


parser = StrictRESTParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs


@parser.error_handler
def handle_request_parsing_error(err, req, schema):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)


def get_pg_error_msg(e):
    parts = str(e).split('\n')
    return None if len(parts) == 0 else parts[0]


def datetime_from_date(date, tzinfo=None):
    return datetime.combine(date, time(tzinfo=tzinfo))
