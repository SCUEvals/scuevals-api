from sqlalchemy.dialects.postgresql import ranges, ExcludeConstraint

from . import db


class Quarter(db.Model):
    __tablename__ = 'quarters'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    current = db.Column(db.Boolean, default=False)
    period = db.Column(ranges.DATERANGE, nullable=False)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    sections = db.relationship('Section', back_populates='quarter')
    university = db.relationship('University', back_populates='quarters')

    __table_args__ = (
        ExcludeConstraint(('period', '&&')),
        db.UniqueConstraint('year', 'name', 'university_id'),
        db.CheckConstraint(name.in_(['Fall', 'Winter', 'Spring', 'Summer']), name='valid_quarter')
    )
