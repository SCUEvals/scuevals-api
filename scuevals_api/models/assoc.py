from . import db

section_professor = db.Table('section_professor', db.metadata,
                             db.Column('section_id', db.Integer, db.ForeignKey('sections.id', ondelete='cascade')),
                             db.Column('professor_id', db.Integer, db.ForeignKey('professors.id', ondelete='cascade')),
                             db.UniqueConstraint('section_id', 'professor_id'))

user_permission = db.Table('user_permission', db.metadata,
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade')),
                           db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id', ondelete='cascade')),
                           db.UniqueConstraint('user_id', 'permission_id'))

api_key_permission = db.Table('api_key_permission', db.metadata,
                              db.Column('api_key_id', db.Integer, db.ForeignKey('api_keys.id', ondelete='cascade')),
                              db.Column('permission_id', db.Integer,
                                        db.ForeignKey('permissions.id', ondelete='cascade')),
                              db.UniqueConstraint('api_key_id', 'permission_id'))

flag_reason = db.Table('flag_reason', db.metadata,
                       db.Column('flag_id', db.Integer, db.ForeignKey('flags.id', ondelete='cascade')),
                       db.Column('reason_id', db.Integer, db.ForeignKey('reasons.id', ondelete='cascade')),
                       db.UniqueConstraint('flag_id', 'reason_id'))

department_major = db.Table('department_major', db.metadata,
                            db.Column('department_id', db.Integer, db.ForeignKey('departments.id', ondelete='cascade')),
                            db.Column('major_id', db.Integer, db.ForeignKey('majors.id', ondelete='cascade')),
                            db.UniqueConstraint('department_id', 'major_id'))


class StudentMajor(db.Model):
    __tablename__ = 'student_major'

    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='cascade'), primary_key=True)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id', ondelete='cascade'), primary_key=True)
    index = db.Column(db.Integer, nullable=False)

    student = db.relationship('Student', back_populates='_majors')
    major = db.relationship('Major', back_populates='_students')

    __table_args_ = (db.UniqueConstraint('student_id', 'major_id', 'index'),)
