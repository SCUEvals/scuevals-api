from sqlalchemy import func
from sqlalchemy.sql import expression

from . import db
from .assoc import flag_reason


class Flag(db.Model):
    __tablename__ = 'flags'

    id = db.Column(db.Integer, primary_key=True)
    flag_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    read = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
    comment = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='set null'), nullable=True)
    accused_student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='cascade'), nullable=False)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id', ondelete='set null'), nullable=True)

    user = db.relationship('User', back_populates='flags')
    reasons = db.relationship('Reason', secondary=flag_reason, back_populates='flags')
    accused_student = db.relationship('Student', back_populates='accused_flags', foreign_keys=[accused_student_id])
    evaluation = db.relationship('Evaluation', back_populates='flags')

    __table_args__ = (
        db.UniqueConstraint(user_id, evaluation_id),
    )
