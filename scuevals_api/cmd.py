from scuevals_api import app, db


@app.cli.command(short_help='Initializes the DB.')
def initdb():

    import scuevals_api.models
    db.create_all()
    db.session.commit()
