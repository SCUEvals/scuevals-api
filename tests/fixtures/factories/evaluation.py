import factory

from .professor import ProfessorFactory
from .section import SectionFactory
from .student import StudentFactory
from scuevals_api import models
from scuevals_api.resources.evaluations import EvaluationSchemaV1

eval_v1_data = {
    'attitude': 1,
    'availability': 1,
    'clarity': 1,
    'grading_speed': 1,
    'resourcefulness': 1,
    'easiness': 1,
    'workload': 1,
    'recommended': 1,
    'comment': 'Love the lectures'
}

EvaluationSchemaV1().load(data=eval_v1_data)


class EvaluationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Evaluation
        sqlalchemy_session = models.db.session

    version = 1
    data = eval_v1_data
    display_grad_year = True
    display_majors = True

    student = factory.SubFactory(StudentFactory)
    professor = factory.SubFactory(ProfessorFactory)
    section = factory.SubFactory(SectionFactory)
