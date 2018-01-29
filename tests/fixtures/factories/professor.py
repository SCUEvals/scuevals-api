import factory

from scuevals_api import models


class ProfessorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Professor
        sqlalchemy_session = models.db.session

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    university_id = 1
