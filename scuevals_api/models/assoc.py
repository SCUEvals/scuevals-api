from . import db

section_professor = db.Table('section_professor', db.metadata,
                             db.Column('section_id', db.Integer, db.ForeignKey('sections.id', ondelete='cascade')),
                             db.Column('professor_id', db.Integer, db.ForeignKey('professors.id')),
                             db.UniqueConstraint('section_id', 'professor_id'))

student_major = db.Table('student_major', db.metadata,
                         db.Column('student_id', db.Integer, db.ForeignKey('students.id', ondelete='cascade')),
                         db.Column('major_id', db.Integer, db.ForeignKey('majors.id')),
                         db.UniqueConstraint('student_id', 'major_id'))

user_permission = db.Table('user_permission', db.metadata,
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade')),
                           db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id')),
                           db.UniqueConstraint('user_id', 'permission_id'))

api_key_permission = db.Table('api_key_permission', db.metadata,
                              db.Column('api_key_id', db.Integer, db.ForeignKey('api_keys.id', ondelete='cascade')),
                              db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id')),
                              db.UniqueConstraint('api_key_id', 'permission_id'))
