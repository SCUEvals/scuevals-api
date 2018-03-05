from . import db, user_permission


class Permission(db.Model):
    Incomplete = 0
    Read = 1
    Write = 2
    Administrator = 10
    API_Key = 20

    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    users = db.relationship('User', secondary=user_permission, back_populates='permissions')
