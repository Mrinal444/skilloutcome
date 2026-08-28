"""Train time-aware placement and attrition models."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.frozen import FrozenEstimator
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, confusion_matrix, f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from src.modeling.features import ATTRITION_CATEGORICAL_FEATURES, ATTRITION_FEATURES, ATTRITION_NUMERIC_FEATURES, ATTRITION_TEXT_FEATURE, MODEL_BUNDLE_SCHEMA_VERSION, PLACEMENT_CATEGORICAL_FEATURES, PLACEMENT_FEATURES, PLACEMENT_NUMERIC_FEATURES, PLACEMENT_TEXT_FEATURE, TEXT_ENCODING_VERSION, build_attrition_frame, build_placement_frame, feature_contract_fingerprint, validate_snapshot

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
RANDOM_STATE = 26135
PLACEMENT_SELECTION_METRIC = "roc_auc"
# Attrition is a rare-event ranking problem, so candidates compete on average precision.
ATTRITION_SELECTION_METRIC = "average_precision"
# Isotonic calibration needs a few hundred positives before it stops fitting noise.
CALIBRATION_ISOTONIC_MIN_POSITIVES = 1000


def _preprocessor(numeric: list[str], categorical: list[str], text: str) -> ColumnTransformer:
    return ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ("skills", TfidfVectorizer(ngram_range=(1, 1), min_df=5, max_features=64), text),
    ], remainder="drop")


def _candidate_factories(y_train: pd.Series) -> dict[str, Callable[[], object]]:
    """Plain and class-weighted variants of each algorithm, so rare positives stay usable."""
    positives = max(int(y_train.sum()), 1)
    imbalance = round(max((len(y_train) - positives) / positives, 1.0), 3)
    return {
        "logistic_regression": lambda: LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "logistic_regression_balanced": lambda: LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
        "random_forest": lambda: RandomForestClassifier(n_estimators=250, min_samples_leaf=3, random_state=RANDOM_STATE, n_jobs=-1),
        "random_forest_balanced": lambda: RandomForestClassifier(n_estimators=250, min_samples_leaf=3, class_weight="balanced_subsample", random_state=RANDOM_STATE, n_jobs=-1),
        "xgboost": lambda: XGBClassifier(n_estimators=250, max_depth=5, learning_rate=0.06, subsample=0.85, colsample_bytree=0.85, eval_metric="logloss", random_state=RANDOM_STATE, n_jobs=-1),
        "xgboost_weighted": lambda: XGBClassifier(n_estimators=250, max_depth=5, learning_rate=0.06, subsample=0.85, colsample_bytree=0.85, eval_metric="logloss", scale_pos_weight=imbalance, random_state=RANDOM_STATE, n_jobs=-1),
    }


def _metrics(y_true: pd.Series, probability: np.ndarray, threshold: float = 0.5) -> dict[str, object]:
    prediction = (probability >= threshold).astype(int)
    return {
        "threshold": round(float(threshold), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probability)), 4),
        "average_precision": round(float(average_precision_score(y_true, probability)), 4),
        "positive_rate_baseline_average_precision": round(float(y_true.mean()), 4),
        "accuracy": round(float(accuracy_score(y_true, prediction)), 4),
        "precision": round(float(precision_score(y_true, prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, prediction, zero_division=0)), 4),
        "brier_score": round(float(brier_score_loss(y_true, probability)), 4),
        "confusion_matrix": confusion_matrix(y_true, prediction).tolist(),
    }


def _f1_optimal_threshold(y_true: pd.Series, score: np.ndarray) -> float:
    """Score cut-off that maximises F1 for the positive class of `score`."""
    precision, recall, thresholds = precision_recall_curve(y_true, score)
    f1 = 2 * precision[:-1] * recall[:-1] / (precision[:-1] + recall[:-1] + 1e-9)
    return float(thresholds[int(np.argmax(f1))])


def _band_summary(y_true: pd.Series, bands: np.ndarray, positive_label_name: str) -> dict[str, object]:
    """Rows and observed outcome rate per band, so band separation is documented, not assumed."""
    frame = pd.DataFrame({"band": bands, "label": np.asarray(y_true)})
    summary = {name: {"rows": int(len(group)), f"observed_{positive_label_name}_rate": round(float(group["label"].mean()), 4)} for name, group in frame.groupby("band")}
    return {"positive_label": positive_label_name, "bands": {name: summary[name] for name in ["low", "medium", "high"] if name in summary}}


def _risk_bands(probability: np.ndarray, medium: float, high: float) -> np.ndarray:
    """Rising probability means rising risk (attrition)."""
    return np.where(probability >= high, "high", np.where(probability >= medium, "medium", "low"))


def _support_bands(probability: np.ndarray, medium: float, high: float) -> np.ndarray:
    """Falling placement probability means rising need for support, so the cuts invert."""
    return np.where(probability <= high, "high", np.where(probability <= medium, "medium", "low"))


def _calibrate(base: Pipeline, X_calibration: pd.DataFrame, y_calibration: pd.Series) -> tuple[CalibratedClassifierCV, str]:
    """Map raw scores onto probabilities using a split the base estimator never saw."""
    method = "isotonic" if int(y_calibration.sum()) >= CALIBRATION_ISOTONIC_MIN_POSITIVES else "sigmoid"
    # In scikit-learn 1.9, ``ensemble='auto'`` selects the single-calibrator path
    # for FrozenEstimator. ``cv=5`` only obtains validation-window predictions;
    # the frozen base model's ``fit`` is a no-op and one calibrator is fit on all
    # validation rows. The test suite guards these semantics.
    calibrated = CalibratedClassifierCV(estimator=FrozenEstimator(base), method=method, cv=5)
    calibrated.fit(X_calibration, y_calibration)
    return calibrated, method


def _time_split(frame: pd.DataFrame, target: pd.Series, date_column: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series, dict[str, str]]:
    dates = pd.to_datetime(frame[date_column])
    validation_start = dates.quantile(0.70)
    test_start = dates.quantile(0.85)
    train_mask = dates < validation_start
    validation_mask = (dates >= validation_start) & (dates < test_start)
    test_mask = dates >= test_start
    if min(train_mask.sum(), validation_mask.sum(), test_mask.sum()) == 0:
        raise ValueError("Time split produced an empty partition.")
    for name, mask in [("train", train_mask), ("validation", validation_mask), ("test", test_mask)]:
        if target.loc[mask].nunique() < 2:
            raise ValueError(f"Time split produced a single-class {name} partition.")
    return frame.loc[train_mask], frame.loc[validation_mask], frame.loc[test_mask], target.loc[train_mask], target.loc[validation_mask], target.loc[test_mask], {"train_before": validation_start.date().isoformat(), "validation_before": test_start.date().isoformat()}


def _train_binary(frame: pd.DataFrame, target: pd.Series, numeric: list[str], categorical: list[str], text: str, model_name: str, target_description: str, selection_metric: str) -> dict:
    X_train, X_validation, X_test, y_train, y_validation, y_test, boundaries = _time_split(frame, target, "Snapshot_Date")
    comparison: dict[str, dict[str, float]] = {}
    best_name, best_score = "", -np.inf
    for name, factory in _candidate_factories(y_train).items():
        pipeline = Pipeline([("preprocessor", _preprocessor(numeric, categorical, text)), ("model", factory())])
        pipeline.fit(X_train, y_train)
        probability = pipeline.predict_proba(X_validation)[:, 1]
        scores = {"roc_auc": round(float(roc_auc_score(y_validation, probability)), 4), "average_precision": round(float(average_precision_score(y_validation, probability)), 4), "brier_score": round(float(brier_score_loss(y_validation, probability)), 4)}
        comparison[name] = scores
        if scores[selection_metric] > best_score:
            best_name, best_score = name, scores[selection_metric]
    # Both selection metrics are rank based, so calibration cannot change the winner. Fit the
    # winner on the training window, then calibrate it on the later validation window: the served
    # model sees every row, and the probabilities it reports mean something.
    base_pipeline = Pipeline([("preprocessor", _preprocessor(numeric, categorical, text)), ("model", _candidate_factories(y_train)[best_name]())])
    base_pipeline.fit(X_train, y_train)
    calibrated, calibration_method = _calibrate(base_pipeline, X_validation, y_validation)
    validation_probability = calibrated.predict_proba(X_validation)[:, 1]
    test_probability = calibrated.predict_proba(X_test)[:, 1]
    report = {
        "model_name": model_name, "target_description": target_description, "selected_algorithm": best_name,
        "selection_metric": f"validation_{selection_metric}", "model_comparison": comparison,
        "calibration": {
            "method": calibration_method, "fitted_on": "validation split", "base_estimator_rows": int(len(X_train)), "calibration_rows": int(len(X_validation)),
            "test_brier_before": round(float(brier_score_loss(y_test, base_pipeline.predict_proba(X_test)[:, 1])), 4),
            "test_brier_after": round(float(brier_score_loss(y_test, test_probability)), 4),
            "baseline_brier_at_test_positive_rate": round(float(y_test.mean() * (1 - y_test.mean())), 4),
        },
        "test_metrics": _metrics(y_test, test_probability),
        "split_strategy": "time_based", "split_boundaries": boundaries,
        "split_rows": {"train": int(len(X_train)), "validation": int(len(X_validation)), "test": int(len(X_test))},
        "split_positive_rates": {"train": round(float(y_train.mean()), 4), "validation": round(float(y_validation.mean()), 4), "test": round(float(y_test.mean()), 4)},
        "positive_rate": round(float(target.mean()), 4),
        "threshold_selection_note": "Thresholds come from the calibration split, so validation-side recall is optimistic; the test metrics at the same thresholds are the unbiased read.",
    }
    return {"pipeline": calibrated, "report": report, "X_test": X_test, "y_test": y_test, "test_probability": test_probability, "validation_target": y_validation, "validation_probability": validation_probability}


def _save_bundle(name: str, pipeline: Pipeline, report: dict, feature_contract: list[str], source_path: str) -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    bundle = {"pipeline": pipeline, "metadata": {"bundle_schema_version": MODEL_BUNDLE_SCHEMA_VERSION, "trained_at_utc": datetime.now(timezone.utc).isoformat(), "source_path": source_path, "feature_contract": feature_contract, "feature_contract_fingerprint": feature_contract_fingerprint(), "text_encoding_version": TEXT_ENCODING_VERSION, "runtime_versions": {"scikit_learn": sklearn.__version__, "xgboost": xgboost.__version__, "pandas": pd.__version__}, "report": report}}
    joblib.dump(bundle, MODELS_DIR / f"{name}.joblib")
    (REPORTS_DIR / f"{name}_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def train_placement(df: pd.DataFrame, source_path: str) -> dict:
    validate_snapshot(df, {"Placement_Target", "Snapshot_Date", *PLACEMENT_FEATURES})
    result = _train_binary(build_placement_frame(df).assign(Snapshot_Date=df["Snapshot_Date"]), df["Placement_Target"].astype(int), PLACEMENT_NUMERIC_FEATURES, PLACEMENT_CATEGORICAL_FEATURES, PLACEMENT_TEXT_FEATURE, "placement_model", "Placement after training completion", PLACEMENT_SELECTION_METRIC)
    report = result["report"]
    # Most trainees are placed, so a 0.5 cut says "placed" for almost everyone and is useless for
    # deciding who needs help. The operational question is the opposite one: whose placement is
    # unlikely enough to justify counselling? That is a threshold on the minority class, derived
    # from the non-placement score (1 - probability).
    not_placed = 1 - result["validation_target"].to_numpy()
    support_cut = _f1_optimal_threshold(pd.Series(not_placed), 1 - result["validation_probability"])
    high, medium = round(1 - support_cut, 4), round(1 - support_cut / 2, 4)
    report["support_thresholds"] = {"high": high, "medium": medium, "selection": "validation_f1_on_non_placement", "interpretation": "placement probability at or below the cut raises the support priority"}
    test_not_placed = 1 - result["y_test"]
    report["test_metrics_at_high_support_threshold"] = _metrics(test_not_placed, 1 - result["test_probability"], 1 - high)
    report["test_metrics_at_medium_support_threshold"] = _metrics(test_not_placed, 1 - result["test_probability"], 1 - medium)
    report["support_band_distribution_test"] = _band_summary(test_not_placed, _support_bands(result["test_probability"], medium, high), "non_placement")
    _save_bundle("placement_model", result["pipeline"], report, PLACEMENT_FEATURES, source_path)
    return report


def train_attrition(df: pd.DataFrame, source_path: str) -> dict:
    validate_snapshot(df, {"Attrition_Target", "Snapshot_Date", *ATTRITION_FEATURES})
    result = _train_binary(build_attrition_frame(df).assign(Snapshot_Date=df["Snapshot_Date"]), df["Attrition_Target"].astype(int), ATTRITION_NUMERIC_FEATURES, ATTRITION_CATEGORICAL_FEATURES, ATTRITION_TEXT_FEATURE, "attrition_model", "Termination before the 6-month retention milestone", ATTRITION_SELECTION_METRIC)
    high_threshold = _f1_optimal_threshold(result["validation_target"], result["validation_probability"])
    report = result["report"]
    report["risk_thresholds"] = {"medium": round(high_threshold / 2, 4), "high": round(high_threshold, 4), "selection": "validation_f1"}
    # Default 0.5 metrics are misleading for a rare event, so also score at the risk threshold used in production.
    test_probability = result["test_probability"]
    report["test_metrics_at_high_risk_threshold"] = _metrics(result["y_test"], test_probability, high_threshold)
    report["test_metrics_at_medium_risk_threshold"] = _metrics(result["y_test"], test_probability, high_threshold / 2)
    report["risk_band_distribution_test"] = _band_summary(result["y_test"], _risk_bands(test_probability, high_threshold / 2, high_threshold), "attrition")
    _save_bundle("attrition_model", result["pipeline"], report, ATTRITION_FEATURES, source_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train SkillOutcome models from normalized snapshots.")
    parser.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data" / "processed")
    parser.add_argument("--task", choices=["placement", "attrition", "both"], default="both")
    args = parser.parse_args()
    results = {}
    if args.task in {"placement", "both"}:
        path = args.data_dir / "placement_training_snapshot.csv"
        results["placement"] = train_placement(pd.read_csv(path), str(path))
    if args.task in {"attrition", "both"}:
        path = args.data_dir / "attrition_training_snapshot.csv"
        results["attrition"] = train_attrition(pd.read_csv(path), str(path))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
