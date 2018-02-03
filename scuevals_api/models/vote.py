from . import db


class Vote(db.Model):
    UPVOTE = 1
    DOWNVOTE = -1

    SYMBOLS = {UPVOTE: 'u', DOWNVOTE: 'd'}

    __tablename__ = 'votes'

    value = db.Column(db.Integer, nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='cascade'), primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id', ondelete='cascade'), primary_key=True)

    student = db.relationship('Student', back_populates='votes')
    evaluation = db.relationship('Evaluation', back_populates='votes')

    __table_args__ = (db.CheckConstraint(value != 0, name='non_zero_value'),)
