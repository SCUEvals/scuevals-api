import factory

from scuevals_api import models


class APIKeyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.APIKey
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    key = factory.Sequence(lambda n: 'KEY_' + str(n))
    university_id = 1

    @factory.lazy_attribute
    def permissions(self):
        return [
            models.Permission.query.get(models.Permission.UpdateCourses),
            models.Permission.query.get(models.Permission.UpdateDepartments),
            models.Permission.query.get(models.Permission.UpdateMajors)
        ]
