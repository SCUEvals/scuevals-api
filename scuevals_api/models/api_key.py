from sqlalchemy import func

from . import db
from .assoc import api_key_permission
from .permission import Permission


API_KEY_TYPE = 'api_key'


class APIKey(db.Model):
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, nullable=False, unique=True)
    issued_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    university_id = db.Column('university_id', db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='api_keys')
    permissions = db.relationship(
        'Permission', secondary=api_key_permission, back_populates='api_keys', passive_deletes=True
    )

    def _get_permissions(self):
        return [permission.id for permission in self.permissions]

    def _set_permissions(self, value):
        while self.permissions:
            del self.permissions[0]

        for permission_id in value:
            permission = Permission.query.get(permission_id)
            if permission is None:
                raise ValueError('permission does not exist: {}'.format(permission_id))

            self.permissions.append(permission)

    permissions_list = property(_get_permissions,
                                _set_permissions,
                                None,
                                'Property permissions_list is a simple wrapper for permissions relation')

    def identity(self):
        return {
            'id': self.id,
            'university_id': self.university_id,
            'type': API_KEY_TYPE,
            'permissions': self.permissions_list
        }
