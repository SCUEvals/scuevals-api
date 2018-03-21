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

    @factory.post_generation
    def professors(self, create, extracted):
        if not create:
            return

        if extracted:
            for professor in extracted:
                self.professors.append(professor)
        else:
            self.professors.append(ProfessorFactory())
