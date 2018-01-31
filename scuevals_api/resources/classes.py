from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import NotFound

from scuevals_api.models import Role, db, Section, Quarter, Professor, Evaluation
from scuevals_api.roles import role_required


class ClassResource(Resource):

    @jwt_required
    @role_required(Role.Student)
    def get(self, q_id, p_id, c_id):
        ident = get_jwt_identity()
        query = db.session.query(Section).options(
            subqueryload(Section.professors)
        ).filter(
            Section.quarter.has(Quarter.university_id == ident['university_id']),
            Section.quarter_id == q_id,
            Section.course_id == c_id,
            Section.professors.any(Professor.id == p_id)
        )

        section = query.one_or_none()

        if section is None:
            raise NotFound('class does not exist')

        # check if user has posted an eval for this class
        has_posted = db.session.query(
            Evaluation.query.filter_by(professor_id=p_id, section_id=section.id, student_id=ident['id']).exists()
        ).scalar()

        return {
            'course': section.course.to_dict(),
            'quarter': section.quarter.to_dict(),
            'professor': [prof for prof in section.professors if prof.id == p_id][0].to_dict(),
            'user_posted': has_posted
        }
