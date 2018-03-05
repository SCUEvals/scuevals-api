import dredd_hooks as hooks
from flask_jwt_extended import create_access_token

from scuevals_api import create_app, db
from scuevals_api.cmd import init_db
from scuevals_api.models import Permission
from tests import seed_db
from tests.fixtures import factories

stash = {}


@hooks.before_all
def before_all(trans):
    app = create_app('test')

    ctx = app.app_context()
    ctx.push()

    db.drop_all()
    init_db(app, db)
    seed_db(db)

    stash['student'] = factories.StudentFactory(
        id=1,
        permissions=[Permission.query.get(Permission.Read), Permission.query.get(Permission.Write)]
    )

    db.session.commit()

    jwt = create_access_token(identity=stash['student'].to_dict())

    for t in trans:
        t['request']['headers']['Authorization'] = 'Bearer ' + jwt


@hooks.before_each
def before_each(trans):
    db.session.begin_nested()


@hooks.after_each
def after_each(trans):
    db.session.rollback()
    db.session.remove()


@hooks.before('Courses > Post Courses')
@hooks.before('Departments > Post Departments')
@hooks.before('Majors > Post Majors')
def before_api_key(trans):
    user = factories.UserFactory(id=100, roles=[Permission.query.get(Permission.API_Key)])

    db.session.commit()

    jwt = create_access_token(identity=user.to_dict())

    trans['request']['headers']['Authorization'] = 'Bearer ' + jwt


@hooks.before('Evaluations > Get Evaluation Details')
def evaluation(trans):
    factories.EvaluationFactory(id=1, student=stash['student'])
