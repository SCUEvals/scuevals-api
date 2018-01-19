from . import db
from .assoc import section_professor


class Professor(db.Model):
    __tablename__ = 'professors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='professors')
    sections = db.relationship('Section', secondary=section_professor, back_populates='professors')
    evaluations = db.relationship('Evaluation', back_populates='professor')

    __mapper_args__ = {
        'polymorphic_identity': 'p',
    }

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
