"""Threshold and band helpers used to turn probabilities into decisions."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("sklearn")
pytest.importorskip("xgboost")

from src.modeling.train import _band_summary, _f1_optimal_threshold, _risk_bands, _support_bands


def test_f1_optimal_threshold_separates_a_clean_split():
    y_true = pd.Series([0, 0, 0, 1, 1, 1])
    score = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    assert _f1_optimal_threshold(y_true, score) == pytest.approx(0.7)


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
