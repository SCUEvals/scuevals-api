from . import db
from .assoc import user_permission, api_key_permission


class Permission(db.Model):
    Incomplete = 0
    ReadEvaluations = 1
    WriteEvaluations = 2
    VoteOnEvaluations = 3

    UpdateCourses = 100
    UpdateDepartments = 101
    UpdateMajors = 102
    UpdateOfficialUserTypes = 103

    Administrator = 1000

    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    users = db.relationship('User', secondary=user_permission, back_populates='permissions')
    api_keys = db.relationship('APIKey', secondary=api_key_permission, back_populates='permissions')
