import dredd_hooks as hooks

from flask_jwt_extended import create_access_token

from scuevals_api import create_app, db
from scuevals_api.cmd import init_db
from scuevals_api.models import Permission, Vote
from tests import seed_db
from tests.fixtures import factories

stash = {}


@hooks.before_all
def before_all(trans):
    app = create_app('test')

    ctx = app.app_context()
    ctx.push()

    stash['app'] = app

    db.session.close_all()
    db.drop_all()


@hooks.before_each
def before_each(trans):
    init_db(stash['app'], db)
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

    factories.UserFactory.reset_sequence(2)

    db.session.commit()

    jwt = create_access_token(identity=stash['student'].to_dict())

    trans['request']['headers']['Authorization'] = 'Bearer ' + jwt


@hooks.after_each
def after_each(trans):
    db.session.close_all()
    db.drop_all()


@hooks.before('Authentication > Authenticate New/Old User')
def skip_test(trans):
    trans['skip'] = True


@hooks.before('Authentication > Authenticate API Key')
def auth_api_key(trans):
    factories.APIKeyFactory(key='<API_KEY>')
    db.session.commit()


@hooks.before('Courses > Get Course Details')
def course_details(trans):
    course = factories.CourseFactory(id=1)
    section = factories.SectionFactory(course=course)
    ev = factories.EvaluationFactory(section=section, professor=section.professors[0])
    factories.VoteFactory(value=Vote.UPVOTE, student=stash['student'], evaluation=ev)
    db.session.commit()


@hooks.before('Evaluations > Get Evaluation Details')
def evaluation(trans):
    factories.EvaluationFactory(id=1, student=stash['student'])
    db.session.commit()


# @hooks.before('Professors > Get Professor Details')
# def professor_details(trans):
#     prof = factories.ProfessorFactory(id=1)
#     factories.EvaluationFactory(professor=prof)
#     factories.EvaluationFactory(professor=prof)
#     db.session.commit()
