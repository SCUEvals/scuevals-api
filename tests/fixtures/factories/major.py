import factory

from scuevals_api import models


class MajorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Major
        sqlalchemy_session = models.db.session

    name = factory.Sequence(lambda n: "Sample Major " + str(n))
    university_id = 1
