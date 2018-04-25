from . import db
from .assoc import department_major, student_major


class Major(db.Model):
    __tablename__ = 'majors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    departments = db.relationship('Department', secondary=department_major, back_populates='majors')
    students = db.relationship('Student', secondary=student_major, back_populates='majors')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'departments': [dep.id for dep in self.departments]
        }
