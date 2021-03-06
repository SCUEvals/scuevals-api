from . import db
from .assoc import department_major


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    courses = db.relationship('Course', back_populates='department')
    school = db.relationship('School', back_populates='departments')
    majors = db.relationship('Major', secondary=department_major, back_populates='departments')

    __table_args__ = (db.UniqueConstraint('abbreviation', 'school_id'),)

    def to_dict(self):
        return {
            'id': self.id,
            'abbr': self.abbreviation,
            'name': self.name,
            'school': self.school.abbreviation
        }
