create or replace view evaluation_scores as
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