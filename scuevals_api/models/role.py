from . import db, user_role


class Role(db.Model):
    Suspended = -1
    Incomplete = 0
    StudentRead = 1
    StudentWrite = 2
    Administrator = 10
    API_Key = 20

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    users = db.relationship('User', secondary=user_role, back_populates='roles')
