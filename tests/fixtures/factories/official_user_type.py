import factory

from scuevals_api import models


class OfficialUserTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.OfficialUserType
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    university_id = 1
