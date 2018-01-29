import factory

from scuevals_api import models
from .course import CourseFactory
from .quarter import QuarterFactory


class SectionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Section
        sqlalchemy_session = models.db.session

    quarter = factory.SubFactory(QuarterFactory)
    course = factory.SubFactory(CourseFactory)
