from . import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    number = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)

    department = db.relationship('Department', back_populates='courses')
    sections = db.relationship('Section', back_populates='course')

    __table_args__ = (db.UniqueConstraint('department_id', 'number'),)

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'department_id': self.department_id
        }
