from . import db, student_role


class Role(db.Model):
    Incomplete = 0
    Student = 1
    Administrator = 10
    API_Key = 20

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    students = db.relationship('Student', secondary=student_role, back_populates='roles')
