from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

from .flag import Flag
from .vote import Vote
from . import db


class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True)
    post_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    data = db.Column(JSONB, nullable=False)
    display_grad_year = db.Column(db.Boolean, nullable=False, server_default='t')
    display_majors = db.Column(db.Boolean, nullable=False, server_default='t')

    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='cascade'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)

    student = db.relationship('Student', back_populates='evaluations')
    professor = db.relationship('Professor', back_populates='evaluations')
    section = db.relationship('Section', back_populates='evaluations')
    votes = db.relationship('Vote', back_populates='evaluation', passive_deletes=True)
    flags = db.relationship('Flag', back_populates='evaluation', passive_deletes=True)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'professor_id', 'section_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'post_time': self.post_time.isoformat(),
            'data': self.data,
            'votes_score': self.votes_value()
        }

    def user_vote(self, user):
        vote = Vote.query.filter(Vote.student_id == user.id, Vote.evaluation_id == self.id).one_or_none()
        return None if vote is None else Vote.SYMBOLS[vote.value]

    def user_flag(self, user):
        flag = Flag.query.filter_by(user_id=user.id, evaluation_id=self.id).one_or_none()
        return False if flag is None else True

    def votes_value(self):
        return sum(v.value for v in self.votes)
