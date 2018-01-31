import factory

from .professor import ProfessorFactory
from .section import SectionFactory
from .student import StudentFactory
from scuevals_api import models


class EvaluationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Evaluation
        sqlalchemy_session = models.db.session

    version = 1
    data = '{"test": 1}'
    display_grad_year = True
    display_majors = True

    student = factory.SubFactory(StudentFactory)
    professor = factory.SubFactory(ProfessorFactory)
    section = factory.SubFactory(SectionFactory)
