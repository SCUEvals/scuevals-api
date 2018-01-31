import factory
from scuevals_api import models


class QuarterFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Quarter
        sqlalchemy_session = models.db.session

    year = 2018
    name = factory.Iterator(['Fall', 'Winter', 'Spring'])
    current = False
    period = factory.Sequence(lambda n: '[2018-{:02d}-01, 2018-{:02d}-01)'.format((n % 11) + 1, (n % 11) + 2))
    university_id = 1
