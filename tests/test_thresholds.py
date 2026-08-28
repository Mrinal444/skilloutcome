"""Threshold and band helpers used to turn probabilities into decisions."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

pytest.importorskip("sklearn")
pytest.importorskip("xgboost")

from src.modeling.train import _band_summary, _calibrate, _f1_optimal_threshold, _risk_bands, _support_bands


def test_f1_optimal_threshold_separates_a_clean_split():
    y_true = pd.Series([0, 0, 0, 1, 1, 1])
    score = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    assert _f1_optimal_threshold(y_true, score) == pytest.approx(0.7)


def test_calibration_freezes_the_previously_fitted_estimator():
    """Calibration must fit only the probability mapper on the later window."""
    train_x = pd.DataFrame({"score": [0.0, 0.1, 0.8, 0.9]})
    train_y = pd.Series([0, 0, 1, 1])
    calibration_x = pd.DataFrame({"score": [0.05, 0.15, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.85, 0.95]})
    calibration_y = pd.Series([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
    base = Pipeline([("model", LogisticRegression(random_state=26135))]).fit(train_x, train_y)
    base_model = base.named_steps["model"]
    coefficients_before = base_model.coef_.copy()
    intercept_before = base_model.intercept_.copy()
    classes_before = base_model.classes_.copy()
    predictions_before = base.predict_proba(calibration_x).copy()

    calibrated, method = _calibrate(base, calibration_x, calibration_y)

    assert method == "sigmoid"
    assert calibrated.cv == 5
    # FrozenEstimator makes ``ensemble='auto'`` use one calibrator fit on the
    # whole calibration window; the original training-window model is untouched.
    assert len(calibrated.calibrated_classifiers_) == 1
    np.testing.assert_array_equal(base_model.coef_, coefficients_before)
    np.testing.assert_array_equal(base_model.intercept_, intercept_before)
    np.testing.assert_array_equal(base_model.classes_, classes_before)
    np.testing.assert_allclose(base.predict_proba(calibration_x), predictions_before)
    probabilities = calibrated.predict_proba(calibration_x)[:, 1]
    assert np.all((probabilities >= 0) & (probabilities <= 1))


def test_risk_bands_rise_with_probability():
    bands = _risk_bands(np.array([0.01, 0.06, 0.20]), medium=0.05, high=0.10)
    assert bands.tolist() == ["low", "medium", "high"]


def test_support_bands_rise_as_placement_probability_falls():
    # medium/high are placement probabilities, so the high-priority cut is the *lower* number.
    bands = _support_bands(np.array([0.90, 0.45, 0.20]), medium=0.60, high=0.30)
    assert bands.tolist() == ["low", "medium", "high"]
    # A probability exactly on a cut belongs to the more urgent band.
    assert _support_bands(np.array([0.30, 0.60]), medium=0.60, high=0.30).tolist() == ["high", "medium"]


def test_band_summary_reports_rows_and_observed_rate_in_band_order():
    y_true = pd.Series([0, 0, 0, 0, 1, 0, 1, 1])
    bands = np.array(["low", "low", "low", "low", "medium", "medium", "high", "high"])
    summary = _band_summary(y_true, bands, "attrition")
    assert summary["positive_label"] == "attrition"
    assert list(summary["bands"]) == ["low", "medium", "high"]
    assert summary["bands"]["low"] == {"rows": 4, "observed_attrition_rate": 0.0}
    assert summary["bands"]["medium"] == {"rows": 2, "observed_attrition_rate": 0.5}
    assert summary["bands"]["high"] == {"rows": 2, "observed_attrition_rate": 1.0}
