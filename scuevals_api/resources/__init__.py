from flask import Blueprint
from flask_restful import Api

from .professors import ProfessorsResource, ProfessorResource
from .courses import CoursesResource, CourseResource
from .departments import DepartmentsResource
from .evaluations import EvaluationsResource, EvaluationResource, EvaluationUpVoteResource, EvaluationDownVoteResource
from .majors import MajorsResource
from .quarters import QuartersResource
from .search import SearchResource
from .students import StudentsResource


resources_bp = Blueprint('resources', __name__)
api = Api(resources_bp)

api.add_resource(CoursesResource, '/courses')
api.add_resource(CourseResource, '/courses/<int:c_id>')

api.add_resource(DepartmentsResource, '/departments')

api.add_resource(EvaluationsResource, '/evaluations')
api.add_resource(EvaluationResource, '/evaluations/<int:e_id>')
api.add_resource(EvaluationUpVoteResource, '/evaluations/<int:e_id>/upvote')
api.add_resource(EvaluationDownVoteResource, '/evaluations/<int:e_id>/downvote')

api.add_resource(MajorsResource, '/majors')

api.add_resource(ProfessorsResource, '/professors')
api.add_resource(ProfessorResource, '/professors/<int:p_id>')

api.add_resource(SearchResource, '/search')
api.add_resource(StudentsResource, '/students/<int:s_id>')
api.add_resource(QuartersResource, '/quarters')
