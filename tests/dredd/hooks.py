import json

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

    if 'real' not in trans or 'body' not in trans['real']:
        return

    data = json.loads(trans['real']['body'])
    if isinstance(data, (list,)):
        if len(data) == 0:
            trans['fail'] = "Empty array returned, nothing was verified"


@hooks.before('Authentication > Authenticate New/Old User')
def skip_test(trans):
    trans['skip'] = True


@hooks.before('Authentication > Authenticate API Key')
def auth_api_key(trans):
    factories.APIKeyFactory(key='<API_KEY>')
    db.session.commit()


@hooks.before('Classes > Get Class Details')
def class_details(trans):
    q = factories.QuarterFactory(id=1)
    c = factories.CourseFactory(id=1)
    prof = factories.ProfessorFactory(id=1)
    factories.QuarterFactory.reset_sequence(2)
    factories.CourseFactory.reset_sequence(2)
    factories.ProfessorFactory.reset_sequence(2)
    factories.SectionFactory(quarter=q, course=c, professors=[prof])
    db.session.commit()


@hooks.before('Courses > List All Courses')
def courses(trans):
    factories.CourseFactory()
    db.session.commit()


@hooks.before('Courses > List Top Courses')
def courses_top(trans):
    s1 = factories.SectionFactory()
    s2 = factories.SectionFactory()

    factories.EvaluationFactory(section=s1)
    factories.EvaluationFactory(section=s1)
    factories.EvaluationFactory(section=s2)
    db.session.commit()


@hooks.before('Courses > Post Courses')
def post_course(trans):
    factories.QuarterFactory(id=1)
    factories.DepartmentFactory(abbreviation='ANTH')
    db.session.commit()


@hooks.before('Courses > Get Course Details')
def course_details(trans):
    course = factories.CourseFactory(id=1)
    section = factories.SectionFactory(course=course)
    ev = factories.EvaluationFactory(section=section, professor=section.professors[0])
    factories.VoteFactory(value=Vote.UPVOTE, student=stash['student'], evaluation=ev)
    db.session.commit()


@hooks.before('Departments > List All Departments')
def departments(trans):
    factories.DepartmentFactory()
    db.session.commit()


@hooks.before('Evaluations > List All Evaluations')
def evaluations(trans):
    prof = factories.ProfessorFactory(id=1)
    course = factories.CourseFactory(id=1)
    quarter = factories.QuarterFactory(id=1)
    factories.QuarterFactory.reset_sequence(2)
    factories.CourseFactory.reset_sequence(2)
    factories.ProfessorFactory.reset_sequence(2)
    sec = factories.SectionFactory(quarter=quarter, course=course, professors=[prof])
    ev = factories.EvaluationFactory(section=sec, professor=prof)
    factories.VoteFactory(value=Vote.UPVOTE, student=stash['student'], evaluation=ev)
    db.session.commit()


@hooks.before('Evaluations > List Recent Evaluations')
def evaluations_recent(trans):
    factories.EvaluationFactory()
    db.session.commit()


@hooks.before('Evaluations > Get Evaluation Details')
def evaluation(trans):
    factories.EvaluationFactory(id=1, student=stash['student'])
    db.session.commit()


@hooks.before('Evaluations > Submit Evaluation')
def evaluations_submit(trans):
    prof = factories.ProfessorFactory(id=1)
    course = factories.CourseFactory(id=1)
    quarter = factories.QuarterFactory(id=1)
    factories.QuarterFactory(current=True)

    factories.SectionFactory(quarter=quarter, course=course, professors=[prof])
    db.session.commit()


@hooks.before('Evaluations > Delete Evaluation')
def evaluations_delete(trans):
    factories.EvaluationFactory(id=1, student=stash['student'])
    db.session.commit()


@hooks.before('Evaluation Votes > Add/Overwrite Vote')
def evaluation_votes_add(trans):
    factories.EvaluationFactory(id=1)
    db.session.commit()


@hooks.before('Evaluation Votes > Delete Vote')
def evaluation_votes_delete(trans):
    ev = factories.EvaluationFactory(id=1)
    factories.VoteFactory(evaluation=ev, student=stash['student'])
    db.session.commit()


@hooks.before('Evaluation Flags > Add Flag')
def evaluation_flags_add(trans):
    factories.EvaluationFactory(id=1)
    db.session.commit()


@hooks.before('Majors > List All Majors')
def majors(trans):
    factories.MajorFactory()
    db.session.commit()


@hooks.before('Professors > List All Professors')
def professors(trans):
    prof = factories.ProfessorFactory()
    course = factories.CourseFactory(id=1)
    quarter = factories.QuarterFactory(id=1)
    section = factories.SectionFactory(course=course, quarter=quarter)
    ev = factories.EvaluationFactory(section=section, professor=prof)
    factories.VoteFactory(value=Vote.UPVOTE, student=stash['student'], evaluation=ev)
    db.session.commit()


@hooks.before('Professors > Get Professor Details')
def professor_details(trans):
    prof = factories.ProfessorFactory(id=1)
    factories.SectionFactory(professors=[prof])
    db.session.commit()


@hooks.before('Quarters > List All Quarters')
def quarters(trans):
    quarter = factories.QuarterFactory()
    course = factories.CourseFactory(id=1)
    prof = factories.ProfessorFactory(id=1)
    factories.SectionFactory(quarter=quarter, course=course, professors=[prof])
    factories.QuarterFactory(current=True)
    db.session.commit()


@hooks.before('Search > Search For Classes And Professors')
def search(trans):
    factories.CourseFactory(title='Mathematics and Such')
    factories.ProfessorFactory(first_name='Matthew')
    db.session.commit()


@hooks.before('Student > Update Info')
def student_update_info(trans):
    factories.MajorFactory(id=1)
    factories.MajorFactory(id=4)
    db.session.commit()


@hooks.before('Student > List All Evaluations')
def student_evaluations(trans):
    prof = factories.ProfessorFactory(id=1)
    course = factories.CourseFactory(id=1)
    quarter = factories.QuarterFactory(id=1)
    sec = factories.SectionFactory(quarter=quarter, course=course, professors=[prof])
    ev = factories.EvaluationFactory(section=sec, professor=prof, student=stash['student'])
    factories.VoteFactory(value=Vote.UPVOTE, student=stash['student'], evaluation=ev)
    db.session.commit()
