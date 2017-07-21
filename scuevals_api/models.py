from sqlalchemy.dialects.postgresql import JSONB
from scuevals_api import db


quarter_course = db.Table('quarter_course', db.metadata,
                          db.Column('quarter_id', db.Integer, db.ForeignKey('quarter.id')),
                          db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                          db.UniqueConstraint('quarter_id', 'course_id', name='quarter_course_uix'))


class EDF(db.Model):
    __tablename__ = 'edf'

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('edf_type.id'), nullable=False)
    url = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime(timezone=True), nullable=False)
    arguments = db.Column(JSONB)
    data = db.Column(JSONB, nullable=False)
    current = db.Column(db.Boolean, default=False)

    type = db.relationship('EDFType', back_populates='edfs')


class EDFType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    edfs = db.relationship('EDF', back_populates='type')

    def __init__(self, idx, name):
        self.id = idx
        self.name = name


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)

    students = db.relationship('Student', back_populates='university')
    professors = db.relationship('Professor', back_populates='university')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text)
    graduation_year = db.Column(db.Integer, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)

    university = db.relationship('University', back_populates='students')
    evaluations = db.relationship('Evaluation', back_populates='student')


class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)

    university = db.relationship('University', back_populates='professors')
    evaluations = db.relationship('Evaluation', back_populates='professor')


class Quarter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    current = db.Column(db.Boolean, default=False)

    evaluations = db.relationship('Evaluation', back_populates='quarter')
    courses = db.relationship('Course', secondary=quarter_course, back_populates="quarters")

    check = db.CheckConstraint(name.in_(['Fall', 'Winter', 'Spring', 'Summer']))


class Evaluation(db.Model):
    __table_args__ = (
        db.UniqueConstraint('student_id', 'professor_id', 'quarter_id', 'course_id', name='uix_evaluation'),
    )

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    quarter_id = db.Column(db.Integer, db.ForeignKey('quarter.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    student = db.relationship('Student', back_populates='evaluations')
    professor = db.relationship('Professor', back_populates='evaluations')
    quarter = db.relationship('Quarter', back_populates='evaluations')
    course = db.relationship('Course', back_populates='evaluations')


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    school = db.Column(db.Text, nullable=False)

    courses = db.relationship('Course', back_populates='department')


class Course(db.Model):
    __table_args__ = (db.UniqueConstraint('department_id', 'number', name='uix_course'),)

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    number = db.Column(db.Text, nullable=False)

    department = db.relationship('Department', back_populates='courses')
    evaluations = db.relationship('Evaluation', back_populates='course')
    quarters = db.relationship('Quarter', secondary=quarter_course, back_populates="courses")
