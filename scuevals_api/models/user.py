from sqlalchemy import func

from . import db
from .role import Role
from .assoc import user_role


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text)
    picture = db.Column(db.Text)
    type = db.Column(db.String(1), nullable=False, server_default='u')
    signup_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    suspended_until = db.Column(db.DateTime(timezone=True))

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='users')
    roles = db.relationship('Role', secondary=user_role, back_populates='users', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'u',
        'polymorphic_on': type
    }

    __table_args__ = (db.CheckConstraint(type.in_(['s', 'p', 'u']), name='user_type'),)

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

    roles_list = property(_get_roles,
                          _set_roles,
                          None,
                          'Property roles_list is a simple wrapper for roles relation')
