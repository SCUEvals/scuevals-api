from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ranges, ExcludeConstraint

db = SQLAlchemy()


section_professor = db.Table('section_professor', db.metadata,
                             db.Column('section_id', db.Integer, db.ForeignKey('sections.id')),
                             db.Column('professor_id', db.Integer, db.ForeignKey('professors.id')),
                             db.UniqueConstraint('section_id', 'professor_id'))


class University(db.Model):
    __tablename__ = 'universities'

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)

    students = db.relationship('Student', back_populates='university')
    professors = db.relationship('Professor', back_populates='university')
    schools = db.relationship('School', back_populates='university')
    quarters = db.relationship('Quarter', back_populates='university')


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text)
    graduation_year = db.Column(db.Integer, nullable=False)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='students')
    evaluations = db.relationship('Evaluation', back_populates='student')


class Professor(db.Model):
    __tablename__ = 'professors'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='professors')
    sections = db.relationship('Section', secondary=section_professor, back_populates='professors')


class Quarter(db.Model):
    __tablename__ = 'quarters'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    current = db.Column(db.Boolean, default=False)
    period = db.Column(ranges.DATERANGE, nullable=False)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    sections = db.relationship('Section', back_populates='quarter')
    university = db.relationship('University', back_populates='quarters')

    __table_args__ = (
        ExcludeConstraint(('period', '&&')),
        db.UniqueConstraint('year', 'name', 'university_id'),
        db.CheckConstraint(name.in_(['Fall', 'Winter', 'Spring', 'Summer']))
    )


class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)

    student = db.relationship('Student', back_populates='evaluations')
    section = db.relationship('Section', back_populates='evaluations')

    __table_args__ = (db.UniqueConstraint('student_id', 'section_id'),)


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    courses = db.relationship('Course', back_populates='department')
    school = db.relationship('School', back_populates='departments')

    __table_args__ = (db.UniqueConstraint('abbreviation', 'school_id', name='departments_abbreviation_school_id_key'),)


class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='schools')
    departments = db.relationship('Department', back_populates='school')


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    number = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)

    department = db.relationship('Department', back_populates='courses')
    sections = db.relationship('Section', back_populates='course')

    __table_args__ = (db.UniqueConstraint('department_id', 'number', name='uix_course'),)


class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)

    quarter_id = db.Column(db.Integer, db.ForeignKey('quarters.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    quarter = db.relationship('Quarter', back_populates='sections')
    course = db.relationship('Course', back_populates='sections')
    professors = db.relationship('Professor', secondary=section_professor, back_populates='sections')
    evaluations = db.relationship('Evaluation', back_populates='section')

    __table_args__ = (db.UniqueConstraint('quarter_id', 'course_id'),)
