import os

import click
from flask.cli import FlaskGroup
from sqlalchemy import text, orm
from sqlalchemy_views import CreateView

from scuevals_api import create_app
from scuevals_api.models import views


def init_db(app, db):
    import scuevals_api.models # noqa
    db.create_all()
    db.session.commit()

    sql_files = ['functions/update_courses.sql', 'functions/update_departments.sql']
    db_dir = os.path.join(os.path.dirname(app.root_path), 'db')

    for sfile in sql_files:
        with open(os.path.join(db_dir, sfile), 'r') as f:
            sql = f.read()
            db.engine.execute(text(sql))

    init_views(db)


def init_views(db):
    for view in views:
        db.engine.execute(CreateView(view.__view__, view.__definition__))

        if not hasattr(view, '_sa_class_manager'):
            orm.mapper(view, view.__view__)


def create_cli_app(pointless_arg):
    """
    A wrapper for create_app that ignores the ScriptInfo object that Click passes.
    """
    return create_app(os.environ.get('FLASK_ENV', default='development'))


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def cli():
    pass
