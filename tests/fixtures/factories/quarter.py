import factory
from math import floor

from scuevals_api import models
from psycopg2.extras import DateRange
from datetime import date, timedelta


class QuarterFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Quarter
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    id = factory.Sequence(lambda n: n)
    year = factory.Sequence(lambda n: 2018 + int(floor(n / 4)))
    name = factory.Iterator(['Fall', 'Winter', 'Spring', 'Summer'])
    period = factory.Sequence(
        lambda n: DateRange(
            date(2018 + int(floor(n / 4)), (n % 4) + 1, 1),
            date(2018 + int(floor(n / 4)), (n % 4) + 2, 1)
        )
    )
    university_id = 1


class QuarterCurrentFactory(QuarterFactory):
    period = DateRange((date.today() + timedelta(days=-1)), (date.today() + timedelta(days=1)))
