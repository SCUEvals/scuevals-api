from . import db


class EvaluationScores(db.Model):
    __table__ = db.Table(
        'evaluation_scores', db.metadata,
        db.Column('evaluation_id', db.Integer, db.ForeignKey('evaluations.id'), primary_key=True),
        db.Column('avg_professor', db.Numeric),
        db.Column('avg_course', db.Numeric),
        db.Column('wavg_total', db.Numeric),
        autoload=True,
        autoload_with=db.engine
    )

    evaluation = db.relationship('Evaluation')
