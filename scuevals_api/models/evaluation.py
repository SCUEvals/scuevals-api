from sqlalchemy.dialects.postgresql import JSONB

from . import db


class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, nullable=False)
    data = db.Column(JSONB, nullable=False)

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

    def votes_value(self):
        return sum(v.value for v in self.votes)
