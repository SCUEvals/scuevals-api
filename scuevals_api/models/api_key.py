from sqlalchemy import func

from . import db


class APIKey(db.Model):
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, nullable=False, unique=True)
    issued_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    university_id = db.Column('university_id', db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='api_keys')