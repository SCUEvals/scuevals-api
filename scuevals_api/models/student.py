from . import db
from .assoc import student_major
from .major import Major
from .user import User


class Student(User):
    __tablename__ = 'students'

    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    graduation_year = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    read_access_exp = db.Column(db.DateTime(timezone=True), nullable=False)

    evaluations = db.relationship('Evaluation', back_populates='student', passive_deletes=True)

    majors = db.relationship('Major', secondary=student_major, back_populates='students', passive_deletes=True)
    votes = db.relationship('Vote', back_populates='student', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 's',
    }

    __table_args__ = (db.CheckConstraint(gender.in_(['m', 'f', 'o']), name='valid_gender'),)

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

    majors_list = property(_get_majors,
                           _set_majors,
                           None,
                           'Property majors_list is a simple wrapper for majors relation')

    def to_dict(self):
        student = {
            'id': self.id,
            'university_id': self.university_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'picture': self.picture,
            'graduation_year': self.graduation_year,
            'majors': self.majors_list,
            'roles': self.roles_list
        }

        return {k: v for k, v in student.items() if v is not None}



