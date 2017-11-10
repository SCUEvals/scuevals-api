from . import db


class University(db.Model):
    __tablename__ = 'universities'

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)

    students = db.relationship('Student', back_populates='university')
    professors = db.relationship('Professor', back_populates='university')
    schools = db.relationship('School', back_populates='university')
    quarters = db.relationship('Quarter', back_populates='university')
    majors = db.relationship('Major', back_populates='university')
    api_keys = db.relationship('APIKey', back_populates='university')
