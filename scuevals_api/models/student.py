from . import db, student_major, student_role, Major, Role


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
    roles = db.relationship('Role', secondary=student_role, back_populates='students')

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

    def _get_roles(self):
        return [role.id for role in self.roles]

    def _set_roles(self, value):
        while self.roles:
            del self.roles[0]

        for role_id in value:
            role = Role.query.get(role_id)
            if role is None:
                raise ValueError('role does not exist: {}'.format(role_id))

            self.roles.append(role)

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

    majors_list = property(_get_majors,
                           _set_majors,
                           None,
                           'Property majors_list is a simple wrapper for majors relation')

    roles_list = property(_get_roles,
                          _set_roles,
                          None,
                          'Property roles_list is a simple wrapper for roles relation')
