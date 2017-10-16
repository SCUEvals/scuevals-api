from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ranges, ExcludeConstraint

db = SQLAlchemy()

section_professor = db.Table('section_professor', db.metadata,
                             db.Column('section_id', db.Integer, db.ForeignKey('sections.id')),
                             db.Column('professor_id', db.Integer, db.ForeignKey('professors.id')),
                             db.UniqueConstraint('section_id', 'professor_id'))

student_major = db.Table('student_major', db.metadata,
                         db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
                         db.Column('major_id', db.Integer, db.ForeignKey('majors.id')),
                         db.UniqueConstraint('student_id', 'major_id'))


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


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text)
    graduation_year = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    picture = db.Column(db.Text)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='students')
    evaluations = db.relationship('Evaluation', back_populates='student')
    majors = db.relationship('Major', secondary=student_major, back_populates='students')

    __table_args__ = (db.CheckConstraint(gender.in_(['m', 'f', 'o'])),)

    def _get_majors(self):
        return [major.id for major in self.majors]

    def _set_majors(self, value):
        while self.majors:
            del self.majors[0]

        for major_id in value:
            major = Major.query.get(major_id)
            if major is None:
                raise ValueError('major does not exist: {}'.format(major_id))

            self.majors.append(major)

    def to_dict(self):
        return {
            'id': self.id,
            'university_id': self.university_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'picture': self.picture,
            'graduation_year': self.graduation_year,
            'majors': self.majors_list
        }

    majors_list = property(_get_majors,
                           _set_majors,
                           None,
                           'Property majors_list is a simple wrapper for majors relation')


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


class Major(db.Model):
    __tablename__ = 'majors'

    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.Text, nullable=False, unique=True)

    university = db.relationship('University', back_populates='majors')
    students = db.relationship('Student', secondary=student_major, back_populates='majors')
