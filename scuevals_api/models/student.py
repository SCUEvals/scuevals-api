from datetime import datetime

from . import db
from .assoc import student_major
from .major import Major
from .user import User
from .permission import Permission


class Student(User):
    __tablename__ = 'students'

    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    graduation_year = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    read_access_until = db.Column(db.DateTime(timezone=True), nullable=True)

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

    def check_read_access(self):
        if self.read_access_until is None:
            return False

        if self.read_access_until >= datetime.now(self.read_access_until.tzinfo):
            return True
        else:
            # the access expired
            self.read_access = False

    def _set_read_access(self, value):
        if value:
            # extend the read access until the set value
            self.read_access_until = value

            # add the read/vote access permissions in case they don't have them
            read = Permission.query.get(Permission.ReadEvaluations)
            vote = Permission.query.get(Permission.VoteOnEvaluations)

            current_permissions = self.permissions_list

            if read not in current_permissions:
                self.permissions.append(read)

            if vote not in current_permissions:
                self.permissions.append(vote)
        else:
            # remove the permissions
            self.permissions = [permission for permission in self.permissions if
                                permission.id not in [Permission.ReadEvaluations, Permission.VoteOnEvaluations]]

            # reset read access tracker
            self.read_access_until = None

    read_access = property(check_read_access,
                           _set_read_access,
                           None,
                           'Property read access is a simple wrapper for controlling reading access')

    def to_dict(self):
        student = {
            **super().to_dict(),
            'gender': self.gender,
            'graduation_year': self.graduation_year,
            'majors': self.majors_list
        }

        return {k: v for k, v in student.items() if v is not None}
