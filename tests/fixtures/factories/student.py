import factory
from datetime import timedelta, datetime, timezone

from .user import UserFactory
from scuevals_api import models
from scuevals_api.utils import datetime_from_date


class StudentFactory(UserFactory):
    class Meta:
        model = models.Student
        sqlalchemy_session = models.db.session

    graduation_year = 2020
    gender = factory.Iterator(['m', 'f', 'o'])
    read_access_until = datetime_from_date(datetime.now() + timedelta(days=180), tzinfo=timezone.utc)

    @factory.lazy_attribute
    def roles(self):
        return [
            models.Role.query.get(models.Role.StudentWrite),
            models.Role.query.get(models.Role.StudentRead)
        ]
