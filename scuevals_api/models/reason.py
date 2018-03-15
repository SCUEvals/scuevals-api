from . import db
from .assoc import flag_reason


class Reason(db.Model):
    __tablename__ = 'reasons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    flags = db.relationship('Flag', secondary=flag_reason, back_populates='reasons')
