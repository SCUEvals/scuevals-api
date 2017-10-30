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
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err)
