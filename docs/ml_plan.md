# SkillOutcome ML workflow

1. `src.data.prepare_dataset` regenerates the normalized tables from the illustrative source and
   validates referential integrity, label balance, leakage boundaries, and snapshot timing before
   committing anything to `data/processed`.
2. Role requirements and assessed skills produce skill coverage, weighted gaps, and ranked
   recommendations. The same `skill_gap_analysis` function serves the API, so the gap features are
   identical in training and production.
3. Demand snapshots join by target role, district, and month.
4. The placement model sees only the training-completion snapshot: training duration, attendance,
   assessment score, blended training performance, prior experience, gap features, local demand,
   course context, provider, certification, internship, target role, and the skills text.
5. The attrition model sees fixed-checkpoint employment snapshots (see `docs/data_model.md`) and
   predicts termination before the six-month retention milestone.
6. Both tasks use chronological 70/15/15 splits by snapshot date, and the split rejects a partition
   that ends up empty or single-class.
7. Six candidates compete per task: logistic regression, random forest, and XGBoost, each in a
   plain and a class-weighted variant. Placement selects on validation ROC-AUC; attrition selects on
   validation average precision, because termination is the rare class and ranking matters more
   than accuracy at 0.5. Both selection metrics are rank-based, so calibration cannot change the
   winner.
8. The winning algorithm is refit on the training window only and then calibrated on the later
   validation window with `CalibratedClassifierCV(cv="prefit")` — isotonic when the calibration
   window holds at least 1000 positives, otherwise sigmoid. The served bundle is the calibrated
   model, so a reported 0.08 means roughly eight in a hundred. `reports/*_metrics.json` records the
   test Brier score before and after calibration next to the baseline Brier at the test positive
   rate, so the gain (or its absence) is visible rather than assumed.
9. Decision thresholds are derived *after* calibration, on the calibration window:
   - Attrition takes the F1-optimal probability as the High boundary and half of it as Medium.
   - Placement inverts the question. At an ~86% placement rate a 0.5 cut labels almost everyone
     "placed" and catches almost no one who needs help, so the threshold is fitted on the minority
     side: the F1-optimal cut on the non-placement score (`1 - probability`). `support_thresholds.high`
     is the placement probability at or below which support priority is High, and `.medium` the
     looser cut. Lower placement probability means higher priority, so the comparisons invert.
   Because thresholds come from the calibration split, validation-side recall at those thresholds is
   optimistic; the test metrics at the same thresholds are the unbiased read, and each report says so
   in `threshold_selection_note`.
10. Both reports record the band distribution on the test window with the *observed* outcome rate per
    band (`risk_band_distribution_test`, `support_band_distribution_test`), so band separation is
    measured rather than asserted, and the model card can cite the numbers directly.
11. `feature_contract_fingerprint()` hashes the feature lists and the skills-tokenisation version
    into each saved bundle. The API refuses to serve a bundle whose fingerprint no longer matches,
    which turns a silent train/serve skew into an explicit 503 and a retrain instruction.

Skills are encoded as one TF-IDF token per skill through `skills_to_text`, so `Power BI` stays a
single `power_bi` token and the token order never varies.

Generated timelines are simulations because the source lacks event dates and real employment
history. Replace generated demand, employment, salary, and engagement records with operational
extracts before deployment.
