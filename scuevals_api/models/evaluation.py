from sqlalchemy.dialects.postgresql import JSONB

from scuevals_api.models.vote import Vote
from . import db


class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, nullable=False)
    data = db.Column(JSONB, nullable=False)
    display_grad_year = db.Column(db.Boolean, nullable=False, server_default='t')
    display_majors = db.Column(db.Boolean, nullable=False, server_default='t')

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)

    student = db.relationship('Student', back_populates='evaluations')
    professor = db.relationship('Professor', back_populates='evaluations')
    section = db.relationship('Section', back_populates='evaluations')
    votes = db.relationship('Vote', back_populates='evaluation')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'professor_id', 'section_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'data': self.data,
            'votes_score': self.votes_value()
        }

    def user_vote(self, user):
        vote = Vote.query.filter(Vote.student_id == user.id, Vote.evaluation_id == self.id).one_or_none()
        return None if vote is None else Vote.SYMBOLS[vote.value]

    def votes_value(self):
        return sum(v.value for v in self.votes)
