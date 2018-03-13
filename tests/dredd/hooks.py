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
        permissions=[
            Permission.query.get(Permission.ReadEvaluations),
            Permission.query.get(Permission.WriteEvaluations),
            Permission.query.get(Permission.VoteOnEvaluations),
            Permission.query.get(Permission.UpdateMajors),
            Permission.query.get(Permission.UpdateDepartments),
            Permission.query.get(Permission.UpdateCourses)
        ]
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


@hooks.before('Evaluations > Get Evaluation Details')
def evaluation(trans):
    factories.EvaluationFactory(id=1, student=stash['student'])


@hooks.before('Authentication > Authenticate API Key')
def auth_new_old_user(trans):
    factories.APIKeyFactory(key='<API_KEY>')
