import factory

from scuevals_api import models


def schools():
    yield from models.School.query.all()


class DepartmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Department
        sqlalchemy_session = models.db.session
        sqlalchemy_session_persistence = 'flush'

    abbreviation = factory.Sequence(lambda n: 'SMPL' + str(n))
    name = 'Sample Department'
    school = factory.iterator(schools)
