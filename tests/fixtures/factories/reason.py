import factory
from scuevals_api import models


class ReasonFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Reason
        sqlalchemy_session = models.db.session

    name = factory.Sequence(lambda n: 'Reason ' + str(n))
