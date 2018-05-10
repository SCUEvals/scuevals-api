from datetime import datetime

import pytz
from sqlalchemy import func, asc
from sqlalchemy.dialects.postgresql import ranges, ExcludeConstraint

from . import db


class Quarter(db.Model):
    __tablename__ = 'quarters'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    period = db.Column(ranges.DATERANGE, nullable=False)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    sections = db.relationship('Section', back_populates='quarter')
    university = db.relationship('University', back_populates='quarters')

    __table_args__ = (
        ExcludeConstraint(('period', '&&')),
        db.UniqueConstraint('year', 'name', 'university_id'),
        db.CheckConstraint(name.in_(['Fall', 'Winter', 'Spring', 'Summer']), name='valid_quarter'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'name': self.name,
            'period': str(self.period),
        }

    @classmethod
    def current(cls):
        return Quarter.query.filter(
            func.upper(Quarter.period) > datetime.now(pytz.timezone('America/Los_Angeles'))
        ).order_by(asc(Quarter.period)).limit(1)
