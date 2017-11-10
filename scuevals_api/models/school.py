from . import db


class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='schools')
    departments = db.relationship('Department', back_populates='school')
