import os

import click
from flask.cli import FlaskGroup
from sqlalchemy import text

from scuevals_api import create_app
from scuevals_api.models import University, School, Role


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


def seed_db(db):
    scu = University(id=1, abbreviation='SCU', name='Santa Clara University')

    db.session.add(scu)
    db.session.add(School(abbreviation='BUS', name='Business', university=scu))
    db.session.add(School(abbreviation='EGR', name='Engineering', university=scu))
    db.session.add(School(abbreviation='AS', name='Arts and Sciences', university=scu))
    db.session.add(School(abbreviation='UNV', name='Generic', university=scu))
    db.session.add(School(abbreviation='CPE', name='Education and Counseling Psychology', university=scu))
    db.session.add(School(abbreviation='LAW', name='Law', university=scu))

    db.session.add(Role(id=0, name='Incomplete'))
    db.session.add(Role(id=1, name='Student'))
    db.session.add(Role(id=2, name='Administrator'))

    db.session.commit()


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    pass
