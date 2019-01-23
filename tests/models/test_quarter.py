from datetime import date

from freezegun import freeze_time
from psycopg2.extras import DateRange

from scuevals_api.models import Quarter
from tests.fixtures.factories import QuarterFactory
from tests import TestCase


class QuarterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.q1 = QuarterFactory(period=DateRange(date(2017, 9, 18), date(2017, 12, 10)))
        self.q2 = QuarterFactory(period=DateRange(date(2018, 1, 8), date(2018, 3, 24)))
        self.q3 = QuarterFactory(period=DateRange(date(2018, 4, 3), date(2018, 6, 15)))

    @freeze_time('2018-01-02', tz_offset=-8)
    def test_current_between(self):
        current = Quarter.current().one()
        self.assertEqual(self.q2, current)

    @freeze_time('2017-10-05', tz_offset=-8)
    def test_current_during(self):
        current = Quarter.current().one()
        self.assertEqual(self.q1, current)
