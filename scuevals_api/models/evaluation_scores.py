from sqlalchemy import text, MetaData

from scuevals_api.models import db
from scuevals_api.db_views import View


class EvaluationScores:
    __view__ = View(
        'evaluation_scores', MetaData(),
        db.Column('evaluation_id', db.Integer, primary_key=True),
        db.Column('avg_professor', db.Numeric),
        db.Column('avg_course', db.Numeric),
        db.Column('wavg_total', db.Numeric)
    )

    __definition__ = text('''
with avgs as (
    select
      id as evaluation_id,
      (
        (data->>'attitude')::numeric +
        (data->>'availability')::numeric +
        (data->>'clarity')::numeric +
        (data->>'grading_speed')::numeric +
        (data->>'resourcefulness')::numeric
      )/5 as avg_professor,
      (
        (data->>'easiness')::numeric +
        (data->>'workload')::numeric
      )/2 as avg_course,
      (data->>'recommended')::numeric as recommended
    from evaluations
    where version=1
)
select
  evaluation_id,
  avg_professor,
  avg_course,
  0.8 * (avg_professor + avg_course)/2 + 0.2 * recommended as wavg_total
from avgs
;
''')
