# Normalized longitudinal data model

| Table | Purpose |
|---|---|
| `trainees` | Trainee identity and demographic context. |
| `training_completions` | Training facts, completion date, and blended training performance. |
| `trainee_skills` | One assessed skill per trainee row, with an assessment date. |
| `role_skill_requirements` | Required skill, proficiency, and importance weight by target role (weights sum to 1). |
| `skill_gap_details` | Derived per-skill deficits and weighted gaps. |
| `job_demand_snapshots` | Role/location/month demand observations. |
| `job_search_events` | Application and interview activity. |
| `employment_spells` | Actual employment start/end records and the termination flag. |
| `salary_history` | Dated salary records. |
| `engagement_checkins` | Dated engagement scores at days 15, 30, 91, and 183 of a spell. |
| `wage_progression_outcomes` | Programme outcome metric: first vs. latest salary and wage growth. |
| `placement_training_snapshot` | Non-leaking placement-model feature view. |
| `attrition_training_snapshot` | Employment-model feature view and attrition label. |

The first eleven are source/event tables; the last two are derived model views. Rows marked
`synthetic_derived` are deterministic derivations and must be replaced with real longitudinal
records before production use.

## Leakage boundaries

`PLACEMENT_FORBIDDEN_COLUMNS` and `ATTRITION_FORBIDDEN_COLUMNS` in `src/modeling/features.py` list
the columns that may never reach a model view, and `prepare_dataset` fails the run if any of them
appear. Wage growth is a deterministic function of the retention label in this source, so it is
published in `wage_progression_outcomes` with `Data_Origin = outcome_metric_not_a_feature` instead
of being offered as a feature.

## Attrition risk window

Each employment spell is observed once, at a fixed checkpoint 30, 60, 90, 120, or 150 days after
the start date. The label is termination before the six-month retention milestone, observed
strictly after that checkpoint. Spells that had already ended by their checkpoint are excluded,
because there is nothing left to predict for them, and the count is reported as
`employment_spells_outside_risk_window` in `reports/data_quality.json`. Because the checkpoint does
not depend on the outcome, `Employment_Duration_Months` cannot encode the label. Salary and
engagement are joined as-of the checkpoint date, never later.

See `docs/input_ownership.md` for the source-system boundary before adding user-facing intake
workflows.
