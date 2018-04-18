from sqlalchemy import MetaData, text, orm

from scuevals_api import db
from scuevals_api.db_views import CreateView, View
from tests import TestCase


class SampleView:
    __view__ = View(
        'sample_view', MetaData(),
        db.Column('bar', db.Text, primary_key=True),
    )

    __definition__ = text('''select 'foo' as bar''')


class DBViewsTestCase(TestCase):
    @classmethod
    def test_drop_view(cls):
        orm.mapper(SampleView, SampleView.__view__)
        db.engine.execute(CreateView(SampleView))
        SampleView.__view__.drop(db.engine)
