import numpy as np
import pytest

from src.validation import (
    cost_sensitive_threshold,
    discrimination_and_calibration,
    population_stability_index,
)


def test_validation_metrics_are_bounded():
    y = np.array([0, 0, 1, 1, 0, 1])
    p = np.array([0.05, 0.15, 0.60, 0.90, 0.30, 0.75])
    m = discrimination_and_calibration(y, p)
    assert 0 <= m["auc"] <= 1
    assert -1 <= m["gini"] <= 1
    assert 0 <= m["ks"] <= 1
    assert 0 <= m["brier"] <= 1


def test_psi_zero_for_identical_samples():
    x = np.linspace(0.01, 0.99, 100)
    assert population_stability_index(x, x) == pytest.approx(0.0)


def test_cost_threshold_returns_valid_threshold():
    y = np.array([0, 0, 0, 1, 1, 1])
    p = np.array([0.05, 0.10, 0.30, 0.40, 0.70, 0.90])
    result = cost_sensitive_threshold(y, p)
    assert 0.01 <= result["threshold"] <= 0.99
