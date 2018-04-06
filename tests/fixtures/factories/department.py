import factory

from scuevals_api import models


def schools():
    yield from models.School.query.all()


class DepartmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Department
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    abbreviation = factory.Iterator(['COEN', 'MATH', 'POLI', 'MECH', 'ELEN'])
    name = 'Sample Department'
    school = factory.iterator(schools)
