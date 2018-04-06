from . import db
from .assoc import flag_reason


class Reason(db.Model):
    Other = 0
    Spam = 1
    Offensive = 2
    SensitiveInfo = 3

    __tablename__ = 'reasons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    flags = db.relationship('Flag', secondary=flag_reason, back_populates='reasons')
