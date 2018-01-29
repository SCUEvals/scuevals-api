import factory

from scuevals_api import models
from .department import DepartmentFactory


class CourseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Course
        sqlalchemy_session = models.db.session

    number = factory.Sequence(lambda n: str(n))
    title = 'What is Life'
    department = factory.SubFactory(DepartmentFactory)
