from scuevals_api import db


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(10))
    name = db.Column(db.String(100))

    students = db.relationship('student', back_populates='university')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    university_id = db.Column(db.Integer, db.ForeignKey('university.id'))
    university = db.relationship('university', back_populates='students')
