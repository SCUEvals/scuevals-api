from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

models_bp = Blueprint('models', __name__)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


@models_bp.record_once
def on_load(state):
    db.init_app(state.app)


from .api_key import APIKey
from .assoc import student_role, student_major, section_professor
from .course import Course
from .department import Department
from .evaluation import Evaluation
from .major import Major
from .professor import Professor
from .quarter import Quarter
from .role import Role
from .school import School
from .section import Section
from .student import Student
from .university import University
from .vote import Vote
