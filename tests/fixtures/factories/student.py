import factory
from datetime import timedelta, datetime

from .user import UserFactory
from scuevals_api import models


class StudentFactory(UserFactory):
    class Meta:
        model = models.Student
        sqlalchemy_session = models.db.session

    graduation_year = 2020
    gender = factory.Iterator(['m', 'f', 'o'])
    read_access_exp = datetime.now() + timedelta(days=180)

    @factory.lazy_attribute
    def roles(self):
        return [
            models.Role.query.get(models.Role.StudentWrite),
            models.Role.query.get(models.Role.StudentRead)
        ]

