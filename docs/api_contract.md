# SkillOutcome API contract

The API is an internal ML service. Callers send values that already exist in the prepared data;
derived features (training performance, skill gap, coverage, demand) are calculated server-side.

## `GET /health`

Reports data and model availability, the expected feature-contract fingerprint, and whether each
saved bundle still matches it. A `false` entry means that model must be retrained before it will
serve.

## `GET /reference/roles`

Target roles the models know, with the required skills, proficiencies, and importance weights used
for gap scoring. An unknown `target_job_role` is rejected with 422.

## `GET /reference/vocabularies`

Controlled values observed in the prepared data for education level, course, training provider,
target and actual job role, employment type, industry, rural/urban, state, and districts by state.
The ingestion layer should bind to these instead of inventing categories.

## `POST /skill-gap`

Provide `target_job_role` plus assessed `current_skills`, each with `name` and `proficiency`. The
API loads role requirements, calculates a weighted gap, and returns missing skills, matched skills,
per-skill deficits, and ranked recommendations. Custom `required_skills` may be provided instead of
a role; one of the two is required.

## `POST /predict-placement`

Required: education level, target job role, assessed skills, attendance, and assessment score.
Optional context (course, provider, duration, prior experience, certification, internship,
rural/urban, state, district) improves the prediction. Returns the calibrated placement probability,
`support_priority` (`High`, `Medium`, or `Low`) with the `support_priority_thresholds` it was applied
against, the skill-gap score, missing skills, recommendations, the selected algorithm, and
`input_warnings`.

`support_priority` is the actionable field. Because most completers are placed, a high probability is
unremarkable; priority rises as the probability *falls*, so `High` means the placement probability is
at or below `support_priority_thresholds.high`. Those cuts are fitted on the calibration split of the
non-placement class, not hard-coded, and they move when the model is retrained.

Example response body (abridged):

```json
{
  "placement_probability": 0.41,
  "placement_probability_percent": 41.0,
  "support_priority": "Medium",
  "support_priority_thresholds": {"high": 0.3421, "medium": 0.6711},
  "skill_gap_score": 18.5,
  "missing_skills": ["Power BI"],
  "model": "logistic_regression",
  "input_warnings": []
}
```

## `POST /predict-attrition`

Required: employment duration, salary, job-history count, and engagement score from
employer/follow-up records. Optional employment, skill, and demand fields improve the prediction.
Returns Low, Medium, or High risk using the bundle's calibration-derived thresholds, the calibrated
probability, the selected algorithm, and `input_warnings`.

Both prediction endpoints serve calibrated probabilities, so the numbers are intended to be read as
rates. `reports/*_metrics.json` records the Brier score before and after calibration and the observed
outcome rate per band; if a band's observed rate is close to the base rate, use the ordering rather
than the absolute number.

## Warnings and failures

`input_warnings` lists categorical values that do not appear in the prepared data. The request still
scores — the model treats the value as unknown — but the warning names the field and points at
`GET /reference/vocabularies` so the caller can fix its mapping instead of guessing. A missing or
stale model returns 503 with the retrain command; an unknown target role returns 422; out-of-range
numbers are rejected by validation with 422.

Open `/docs` while the service is running for the generated OpenAPI schema and examples.
