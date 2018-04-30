from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from . import db
from .assoc import department_major, StudentMajor


class Major(db.Model):
    __tablename__ = 'majors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    departments = db.relationship('Department', secondary=department_major, back_populates='majors')
    _students = db.relationship('StudentMajor',  order_by='StudentMajor.index', collection_class=ordering_list('index'),
                                back_populates='major', passive_deletes=True, cascade="all, delete-orphan")
    students = association_proxy('_students', 'student', creator=lambda student: StudentMajor(student=student))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'departments': [dep.id for dep in self.departments]
        }
