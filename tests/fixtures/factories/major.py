import factory

from tests.fixtures.factories import DepartmentFactory
from scuevals_api import models


class MajorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Major
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Sequence(lambda n: "Sample Major " + str(n))
    departments = factory.List([factory.SubFactory(DepartmentFactory)])
