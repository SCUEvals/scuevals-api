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


from .api_key import APIKey  # noqa
from .assoc import user_role, student_major, section_professor  # noqa
from .course import Course  # noqa
from .department import Department  # noqa
from .evaluation import Evaluation  # noqa
from .major import Major  # noqa
from .professor import Professor  # noqa
from .quarter import Quarter  # noqa
from .role import Role  # noqa
from .school import School  # noqa
from .section import Section  # noqa
from .student import Student  # noqa
from .university import University  # noqa
from .official_user_type import OfficialUserType  # noqa
from .user import User  # noqa
from .vote import Vote  # noqa
