# SkillOutcome model card

## Intended use

Use scores to prioritize support, counselling, job matching, and programme evaluation. Do not use
them as the sole basis for denying an opportunity or service.

## Placement model

Predicts `Placement_Target` from the dated training-completion snapshot: training performance,
assessed skills, calculated role gap, local demand, course context, and relevant experience. It
excludes placement status, salary, actual job, retention, non-placement reason, and any model
probability, all of which are known only after the predicted event.

Roughly 86% of completers are placed, so accuracy and a 0.5 cut-off say almost nothing: predicting
"placed" for everyone already scores in the mid-eighties while catching none of the people who need
help. The model is therefore read two ways. `roc_auc` and `average_precision` in
`reports/placement_model_metrics.json` measure ranking quality, and a **support priority** band
answers the operational question — whose placement is unlikely enough to justify counselling. The
band comes from an F1-optimal threshold fitted on the non-placement score (`1 - probability`) on the
calibration window, stored as `support_thresholds` and applied by `POST /predict-placement`:
placement probability at or below `high` is High priority, at or below `medium` is Medium, otherwise
Low. `test_metrics_at_high_support_threshold` and `test_metrics_at_medium_support_threshold` report
precision and recall *for the non-placement class* at those cuts, and
`support_band_distribution_test` gives the rows and observed non-placement rate per band.

## Attrition model

Predicts termination before the six-month retention milestone, observed at a fixed checkpoint 30 to
150 days into the employment spell. Features are joined as-of that checkpoint, so no feature can
carry information from after it. Spells that had already ended by their checkpoint are outside the
risk window and are excluded from training.

Risk bands are not fixed constants: the High threshold is the F1-optimal calibrated probability on
the calibration window and Medium is half of it, both stored in the model bundle and applied by the
API. Because positives are rare, read `average_precision`, the threshold-specific metrics, and
`brier_score` from `reports/attrition_model_metrics.json` rather than accuracy at 0.5, and read
`risk_band_distribution_test` to see whether the bands actually separate: each band reports its row
count and its observed attrition rate on held-out data.

## Calibration and how to read a probability

The selected algorithm is fit on the training window and then calibrated on the later validation
window, which it never trained on (`CalibratedClassifierCV(cv="prefit")`; isotonic when that window
holds at least 1000 positives, otherwise sigmoid). The bundle that is served is the calibrated model,
so a reported probability is meant to be read as a rate, not just a ranking score. The
`calibration` block in each report shows the test Brier score before and after calibration alongside
`baseline_brier_at_test_positive_rate` — the score a model that always predicts the base rate would
get. A Brier score close to that baseline means the probabilities carry little more information than
the base rate, and the bands should be trusted only for ordering, not as absolute rates.

Thresholds are derived on the calibration split, so validation-side recall at those thresholds is
optimistic. The test metrics at the same thresholds are the unbiased read; each report repeats this
in `threshold_selection_note`.

## Train/serve consistency

Placement and attrition features are defined once in `src/modeling/features.py` and built by the
same functions in training and serving. Each bundle stores a fingerprint of the feature contract
and the skills-tokenisation version; the API returns 503 with a retrain instruction if a bundle no
longer matches the code, and `GET /health` reports the status of each model.

## Data limitation

The provided source has no real dates, job histories, salary records, engagement history, or
external demand feed. The preparation pipeline creates deterministic synthetic tables for
demonstration and marks them `synthetic_derived`. Wage growth is published only as an outcome
metric. Replace these with real operational extracts before policy or production use.
