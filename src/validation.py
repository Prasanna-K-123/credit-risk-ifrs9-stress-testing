from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import logit
from scipy.stats import ks_2samp
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score


def discrimination_and_calibration(y_true, pd_hat) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=int)
    pd_hat = np.clip(np.asarray(pd_hat, dtype=float), 1e-6, 1 - 1e-6)

    auc = roc_auc_score(y_true, pd_hat)
    ks = ks_2samp(pd_hat[y_true == 1], pd_hat[y_true == 0]).statistic
    brier = brier_score_loss(y_true, pd_hat)

    logits = logit(pd_hat).reshape(-1, 1)
    recal = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000)
    recal.fit(logits, y_true)
    calibration_slope = float(recal.coef_[0][0])
    calibration_intercept = float(recal.intercept_[0])

    return {
        "auc": float(auc),
        "gini": float(2 * auc - 1),
        "ks": float(ks),
        "brier": float(brier),
        "calibration_intercept": calibration_intercept,
        "calibration_slope": calibration_slope,
    }


def bootstrap_auc_ci(y_true, pd_hat, n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    y_true = np.asarray(y_true, dtype=int)
    pd_hat = np.asarray(pd_hat, dtype=float)
    rng = np.random.default_rng(seed)
    aucs = []

    for _ in range(n_boot):
        idx = rng.integers(0, len(y_true), len(y_true))
        if len(np.unique(y_true[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y_true[idx], pd_hat[idx]))

    lo, hi = np.quantile(aucs, [0.025, 0.975])
    return float(lo), float(hi)


def cost_sensitive_threshold(
    y_true,
    pd_hat,
    false_negative_cost: float = 5.0,
    false_positive_cost: float = 1.0,
) -> dict[str, float]:
    """Choose a threshold using the classic German-credit asymmetric cost idea.

    Here a false negative means an actually bad/defaulting account is accepted.
    """
    y_true = np.asarray(y_true, dtype=int)
    pd_hat = np.asarray(pd_hat, dtype=float)
    best = None

    for threshold in np.linspace(0.01, 0.99, 197):
        pred = (pd_hat >= threshold).astype(int)
        fn = int(((pred == 0) & (y_true == 1)).sum())
        fp = int(((pred == 1) & (y_true == 0)).sum())
        total_cost = false_negative_cost * fn + false_positive_cost * fp
        row = (total_cost, threshold, fn, fp)
        if best is None or row < best:
            best = row

    total_cost, threshold, fn, fp = best
    return {
        "threshold": float(threshold),
        "weighted_cost": float(total_cost),
        "false_negatives": int(fn),
        "false_positives": int(fp),
    }


def population_stability_index(expected, actual, bins: int = 10) -> float:
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    breaks = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(breaks) < 3:
        return 0.0
    breaks[0], breaks[-1] = -np.inf, np.inf

    e_counts, _ = np.histogram(expected, bins=breaks)
    a_counts, _ = np.histogram(actual, bins=breaks)
    e = np.clip(e_counts / e_counts.sum(), 1e-6, None)
    a = np.clip(a_counts / a_counts.sum(), 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))


def pd_to_grade(pd_hat: float) -> str:
    p = float(pd_hat)
    if p < 0.02:
        return "A"
    if p < 0.05:
        return "B"
    if p < 0.10:
        return "C"
    if p < 0.20:
        return "D"
    if p < 0.35:
        return "E"
    return "F"


def grade_distribution(pd_hat) -> dict[str, int]:
    grades = pd.Series([pd_to_grade(v) for v in pd_hat])
    return {k: int(v) for k, v in grades.value_counts().sort_index().items()}
