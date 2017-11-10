import json

from scuevals_api.models import db, Quarter
from tests import TestCase


class QuartersTestCase(TestCase):
    def setUp(self):
        super(QuartersTestCase, self).setUp()

        with self.app.app_context():
            db.session.add(Quarter(id=1, year=2017, name='Winter', current=False,
                                   period='[2017-01-01, 2017-02-01]', university_id=1))
            db.session.add(Quarter(id=2, year=2017, name='Spring', current=False,
                                   period='[2017-03-01, 2017-04-01]', university_id=1))
            db.session.commit()

    def test_quarters(self):
        headers = {'Authorization': 'Bearer ' + self.jwt}

        rv = self.client.get('/quarters', headers=headers)

        self.assertEqual(rv.status_code, 200)

        data = json.loads(rv.data)
        self.assertEqual(len(data), 2)
