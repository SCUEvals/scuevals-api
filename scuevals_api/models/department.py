from . import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    courses = db.relationship('Course', back_populates='department')
    school = db.relationship('School', back_populates='departments')

    __table_args__ = (db.UniqueConstraint('abbreviation', 'school_id'),)
