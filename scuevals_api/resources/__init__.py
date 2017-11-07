from flask import Blueprint
from flask_restful import Api

from .courses import Courses
from .departments import Departments
from .evaluations import Evaluations
from .majors import Majors
from .quarters import Quarters
from .search import Search
from .students import Students


resources_bp = Blueprint('resources', __name__)
api = Api(resources_bp)

api.add_resource(Departments, '/departments')
api.add_resource(Courses, '/courses')
api.add_resource(Quarters, '/quarters')
api.add_resource(Majors, '/majors')
api.add_resource(Search, '/search')
api.add_resource(Students, '/students/<int:s_id>')
api.add_resource(Evaluations, '/evaluations')
