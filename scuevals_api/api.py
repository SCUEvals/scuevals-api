from webargs import fields, missing
from webargs.flaskparser import parser, use_kwargs
from scuevals_api.models import Course, Quarter
from scuevals_api import api
from flask_restful import Resource, abort


class Courses(Resource):
    args = {'quarter_id': fields.Integer()}

    @use_kwargs(args)
    def get(self, quarter_id):

        if quarter_id is missing:
            courses = Course.query.all()
        else:
            courses = Course.query.join(Course.quarters).filter(Quarter.id == quarter_id).all()

        return [
            {
                'id': course.id,
                'department': course.department.abbreviation,
                'number': course.number,
                'title': course.title,
                'quarters': [quarter.id for quarter in course.quarters]
            }
            for course in courses
        ]


class Quarters(Resource):
    def get(self):
        quarters = Quarter.query.all()

        return [
            {
                'id': quarter.id,
                'year': quarter.year,
                'name': quarter.name,
                'current': quarter.current
            }
            for quarter in quarters
        ]


@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)


api.add_resource(Courses, '/courses')
api.add_resource(Quarters, '/quarters')
