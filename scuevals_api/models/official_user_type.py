from . import db


class OfficialUserType(db.Model):
    __tablename__ = 'official_user_type'

    email = db.Column(db.Text, primary_key=True)
    type = db.Column(db.Text, nullable=False)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    university = db.relationship('University', back_populates='official_user_types')

    __table_args__ = (
        db.UniqueConstraint('email', 'type', 'university_id'),
    )
