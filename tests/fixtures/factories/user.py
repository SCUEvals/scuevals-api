import factory

from scuevals_api import models


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.User
        sqlalchemy_session = models.db.session

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda a: '{0}.{1}@scu.edu'.format(a.first_name, a.last_name).lower())
    university_id = 1
