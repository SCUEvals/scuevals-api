from flask import Blueprint
from flask_restful import Api

from .api import APIStatusResource
from .professors import ProfessorsResource, ProfessorsTopResource, ProfessorResource
from .classes import ClassResource
from .courses import CoursesResource, CoursesTopResource, CourseResource
from .departments import DepartmentsResource
from .evaluations import (
    EvaluationsResource, EvaluationsRecentResource, EvaluationResource, EvaluationVoteResource, EvaluationFlagResource
)
from .majors import MajorsResource
from .official_user_types import OfficialUserTypeResource
from .quarters import QuartersResource
from .search import SearchResource
from .students import StudentsResource, StudentEvaluationsResource

resources_bp = Blueprint('resources', __name__)
api = Api(resources_bp)

api.add_resource(APIStatusResource, '/')

api.add_resource(ClassResource, '/classes/<int:q_id>/<int:p_id>/<int:c_id>')

api.add_resource(CoursesResource, '/courses')
api.add_resource(CoursesTopResource, '/courses/top')
api.add_resource(CourseResource, '/courses/<int:c_id>')

api.add_resource(DepartmentsResource, '/departments')

api.add_resource(EvaluationsResource, '/evaluations')
api.add_resource(EvaluationsRecentResource, '/evaluations/recent')
api.add_resource(EvaluationResource, '/evaluations/<int:e_id>')
api.add_resource(EvaluationVoteResource, '/evaluations/<int:e_id>/vote')
api.add_resource(EvaluationFlagResource, '/evaluations/<int:e_id>/flag')

api.add_resource(MajorsResource, '/majors')

api.add_resource(OfficialUserTypeResource, '/official_user_types')

api.add_resource(ProfessorsResource, '/professors')
api.add_resource(ProfessorsTopResource, '/professors/top')
api.add_resource(ProfessorResource, '/professors/<int:p_id>')

api.add_resource(SearchResource, '/search')

api.add_resource(StudentsResource, '/students/<int:s_id>')
api.add_resource(StudentEvaluationsResource, '/students/<int:s_id>/evaluations')

api.add_resource(QuartersResource, '/quarters')
