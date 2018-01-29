import factory
from scuevals_api import models


class DepartmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Department
        sqlalchemy_session = models.db.session

    abbreviation = factory.Iterator(['COEN', 'MATH', 'POLI', 'MECH'])
    name = 'Sample Department'

    @factory.lazy_attribute
    def school(self):
        return models.School.query.first()
