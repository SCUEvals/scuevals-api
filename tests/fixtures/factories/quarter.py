import factory
from math import floor
from scuevals_api import models


class QuarterFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Quarter
        sqlalchemy_session = models.db.session

    year = 2018
    name = factory.Iterator(['Fall', 'Winter', 'Spring', 'Summer'])
    current = False
    period = factory.Sequence(
        lambda n: '[20{:02d}-{:02d}-01, 20{:02d}-{:02d}-01)'.format(
            18 + int(floor(n / 4)),
            (n % 4) + 1,
            18 + int(floor(n / 4)),
            (n % 4) + 2
        )
    )
    university_id = 1
