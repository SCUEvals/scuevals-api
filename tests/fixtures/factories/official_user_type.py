import factory

from scuevals_api import models


class OfficialUserTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.OfficialUserType
        sqlalchemy_session = models.db.session

    university_id = 1
