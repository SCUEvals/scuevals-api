from . import db, student_major


class Major(db.Model):
    __tablename__ = 'majors'

    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.Text, nullable=False, unique=True)

    university = db.relationship('University', back_populates='majors')
    students = db.relationship('Student', secondary=student_major, back_populates='majors')
