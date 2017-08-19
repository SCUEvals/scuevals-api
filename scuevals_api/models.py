from scuevals_api import db
from sqlalchemy.dialects.postgresql import ranges, ExcludeConstraint


quarter_course = db.Table('quarter_course', db.metadata,
                          db.Column('quarter_id', db.Integer, db.ForeignKey('quarter.id')),
                          db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                          db.UniqueConstraint('quarter_id', 'course_id', name='quarter_course_uix'))


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)

    students = db.relationship('Student', back_populates='university')
    professors = db.relationship('Professor', back_populates='university')
    schools = db.relationship('School', back_populates='university')


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
    period = db.Column(ranges.DATERANGE, nullable=False)

    evaluations = db.relationship('Evaluation', back_populates='quarter')
    courses = db.relationship('Course', secondary=quarter_course, back_populates="quarters")

    __table_args__ = (
        ExcludeConstraint(('period', '&&')),
        db.UniqueConstraint('year', 'name'),
        db.CheckConstraint(name.in_(['Fall', 'Winter', 'Spring', 'Summer']))
    )


class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    quarter_id = db.Column(db.Integer, db.ForeignKey('quarter.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    student = db.relationship('Student', back_populates='evaluations')
    professor = db.relationship('Professor', back_populates='evaluations')
    quarter = db.relationship('Quarter', back_populates='evaluations')
    course = db.relationship('Course', back_populates='evaluations')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'professor_id', 'quarter_id', 'course_id', name='uix_evaluation'),
    )


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

    courses = db.relationship('Course', back_populates='department')
    school = db.relationship('School', back_populates='departments')

    __table_args__ = (db.UniqueConstraint('abbreviation', 'school_id', name='uix_department'),)


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)

    university = db.relationship('University', back_populates='schools')
    departments = db.relationship('Department', back_populates='school')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    number = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)

    department = db.relationship('Department', back_populates='courses')
    evaluations = db.relationship('Evaluation', back_populates='course')
    quarters = db.relationship('Quarter', secondary=quarter_course, back_populates="courses")

    __table_args__ = (db.UniqueConstraint('department_id', 'number', name='uix_course'),)
