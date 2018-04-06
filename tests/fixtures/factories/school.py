import factory
from scuevals_api import models


class SchoolFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.School
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    abbreviation = factory.Iterator(['AS', 'BUS', 'EGR'])
    name = factory.Iterator(['Arts and Sciences', 'Business', 'Engineering'])
    university_id = 1
