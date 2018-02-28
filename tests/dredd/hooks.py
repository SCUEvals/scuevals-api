import dredd_hooks as hooks
from flask_jwt_extended import create_access_token

from scuevals_api import create_app, db
from scuevals_api.cmd import init_db
from scuevals_api.models import Role
from tests import seed_db
from tests.fixtures.factories import StudentFactory


@hooks.before_all
def before_all(trans):
    app = create_app('test')

    ctx = app.app_context()
    ctx.push()

    db.drop_all()
    init_db(app, db)
    seed_db(db)

    student = StudentFactory(
        id=0,
        roles=[Role.query.get(Role.Student)]
    )

    ident = student.to_dict()

    db.session.commit()

    jwt = create_access_token(identity=ident)

    for t in trans:
        t['request']['headers']['Authorization'] = 'Bearer ' + jwt


@hooks.before_each
def before_each(trans):
    db.session.begin_nested()


@hooks.after_each
def after_each(trans):
    db.session.rollback()
    db.session.remove()
