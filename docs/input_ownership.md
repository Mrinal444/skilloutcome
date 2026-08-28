# Input ownership and preprocessing boundary

The current API is an internal ML-service contract. It expects normalized values; a trainee should not be asked to manually enter every field.

| Field group | Source | Current use |
|---|---|---|
| Target job role, course, prior experience | Trainee profile or counsellor workflow | Placement context |
| Attendance, assessment score, certification, internship | Training/LMS records | Placement features |
| Skill proficiency | Skill-assessment service | Role-gap calculation |
| Role requirements and importance | Programme/employer configuration | Server-calculated gaps and recommendations |
| Demand score | Job-posting feed by role/location/month | Server-calculated placement feature |
| Salary, employment duration, job history, engagement | Employer and follow-up records | Attrition features |
| Training performance, skill gap, coverage, recommendations | Pipeline | Derived only; never user-entered |
| Placement probability, attrition probability, wage growth | ML/outcome pipeline | Outputs only; never model inputs at the same decision point |

The future ingestion layer should validate source records, map names to controlled vocabularies, deduplicate trainee IDs, calculate derived values, and then build the snapshots consumed by this service. It should not expose the internal feature fields as a raw end-user form.

## How the service enforces the boundary today

`GET /reference/vocabularies` publishes the controlled values the models actually saw — education
levels, courses, providers, target and actual roles, employment types, industries, rural/urban,
states, and districts per state — and `GET /reference/roles` publishes the skill requirements used
for gap scoring. Callers should bind their dropdowns and mappings to those lists.

If a request still carries a category that is absent from the prepared data, the prediction
endpoints answer normally but return an `input_warnings` entry naming the field and the value. The
model treats such a value as unknown, so a warning means the ingestion mapping is wrong, not that
the trainee is unusual. Treat a non-empty `input_warnings` list as a defect in the caller.

Fields in the last two rows of the table above are never accepted from a caller at all: the service
calculates them, or they are outputs. `training_performance` may be supplied only because the LMS
already stores the same blend that `training_performance()` computes; when it is omitted, the API
derives it.

