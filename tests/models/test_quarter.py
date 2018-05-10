from freezegun import freeze_time

from scuevals_api.models import Quarter
from tests.fixtures.factories import QuarterFactory
from tests import TestCase


class QuarterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.q1 = QuarterFactory(period='[2017-09-18,2017-12-10)')
        self.q2 = QuarterFactory(period='[2018-01-08,2018-03-24)')
        self.q3 = QuarterFactory(period='[2018-04-03,2018-06-15)')

    @freeze_time('2018-01-02', tz_offset=-8)
    def test_current_between(self):
        current = Quarter.current().one()
        self.assertEqual(self.q2, current)

    @freeze_time('2017-10-05', tz_offset=-8)
    def test_current_during(self):
        current = Quarter.current().one()
        self.assertEqual(self.q1, current)
