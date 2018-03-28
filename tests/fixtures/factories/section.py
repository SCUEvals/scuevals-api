import factory

from scuevals_api import models
from .course import CourseFactory
from .quarter import QuarterFactory
from .professor import ProfessorFactory


class SectionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Section
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    quarter = factory.SubFactory(QuarterFactory)
    course = factory.SubFactory(CourseFactory)
    professors = factory.List([factory.SubFactory(ProfessorFactory)])
