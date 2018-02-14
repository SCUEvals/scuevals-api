import factory
from datetime import timedelta, datetime

from scuevals_api import models


class StudentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Student
        sqlalchemy_session = models.db.session

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda a: '{0}.{1}@scu.edu'.format(a.first_name, a.last_name).lower())
    graduation_year = 2020
    gender = factory.Iterator(['m', 'f', 'o'])
    read_access_exp = datetime.now() + timedelta(days=180)
    university_id = 1
