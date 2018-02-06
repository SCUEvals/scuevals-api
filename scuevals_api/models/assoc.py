from . import db

section_professor = db.Table('section_professor', db.metadata,
                             db.Column('section_id', db.Integer, db.ForeignKey('sections.id', ondelete='cascade')),
                             db.Column('professor_id', db.Integer, db.ForeignKey('professors.id')),
                             db.UniqueConstraint('section_id', 'professor_id'))

student_major = db.Table('student_major', db.metadata,
                         db.Column('student_id', db.Integer, db.ForeignKey('students.id', ondelete='cascade')),
                         db.Column('major_id', db.Integer, db.ForeignKey('majors.id')),
                         db.UniqueConstraint('student_id', 'major_id'))

user_role = db.Table('user_role', db.metadata,
                     db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade')),
                     db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
                     db.UniqueConstraint('user_id', 'role_id'))
