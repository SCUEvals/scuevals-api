from scuevals_api import app, db
from scuevals_api.models import University, School


@app.cli.command(short_help='Initializes the DB.')
def initdb():
    import scuevals_api.models
    db.create_all()
    db.session.commit()

    sql_files = ['db/insert_courses.sql', 'db/insert_departments.sql']

    for sfile in sql_files:
        with open(sfile, 'r') as f:
            sql = f.read()
            db.engine.execute(sql)


@app.cli.command(short_help='Seeds the DB.')
def seeddb():
    scu = University(abbreviation='SCU', name='Santa Clara University')

    db.session.add(scu)
    db.session.add(School(abbreviation='BUS', name='Business', university=scu))
    db.session.add(School(abbreviation='EGR', name='Engineering', university=scu))
    db.session.add(School(abbreviation='AS', name='Arts and Sciences', university=scu))
    db.session.add(School(abbreviation='UNV', name='Generic', university=scu))
    db.session.add(School(abbreviation='CPE', name='Education and Counseling Psychology', university=scu))
    db.session.add(School(abbreviation='LAW', name='Law', university=scu))

    db.session.commit()
