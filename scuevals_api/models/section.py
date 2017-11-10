from . import db, section_professor


class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)

    quarter_id = db.Column(db.Integer, db.ForeignKey('quarters.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    quarter = db.relationship('Quarter', back_populates='sections')
    course = db.relationship('Course', back_populates='sections')
    professors = db.relationship('Professor', secondary=section_professor, back_populates='sections')
    evaluations = db.relationship('Evaluation', back_populates='section')

    __table_args__ = (db.UniqueConstraint('quarter_id', 'course_id'),)
