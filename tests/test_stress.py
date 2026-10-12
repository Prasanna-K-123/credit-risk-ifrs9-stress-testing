import numpy as np

from src.stress import scenario_portfolio_ecl, stressed_pd


def test_stressed_pd_is_capped():
    p = stressed_pd([0.8, 0.2], 2.0)
    assert np.all(p <= 0.999)


def test_severe_ecl_not_below_base_ecl():
    df = scenario_portfolio_ecl(
        base_pd=[0.05, 0.12, 0.30],
        amounts=[1000, 1500, 2000],
        remaining_months=[12, 24, 36],
        default_flags=[0, 0, 0],
    )
    base = float(df.loc[df["scenario"] == "base", "portfolio_ecl"].iloc[0])
    severe = float(df.loc[df["scenario"] == "severe", "portfolio_ecl"].iloc[0])
    assert severe >= base

def test_vector_validation_rejects_truncation_and_invalid_domains():
    import pytest

    valid = dict(base_pd=[0.05, 0.12], amounts=[100.0, 200.0],
                 remaining_months=[12, 24], default_flags=[0, 1])
    assert scenario_portfolio_ecl(**valid)["portfolio_ead"].eq(300.0).all()
    bad_cases = [
        ({"base_pd": [0.05]}, "equal lengths"),
        ({"amounts": [100.0]}, "equal lengths"),
        ({"remaining_months": [12]}, "equal lengths"),
        ({"default_flags": [0]}, "equal lengths"),
        ({"base_pd": [float("nan"), 0.12]}, "finite"),
        ({"amounts": [float("inf"), 200.0]}, "finite"),
        ({"base_pd": [-0.01, 0.12]}, "PD"),
        ({"base_pd": [1.01, 0.12]}, "PD"),
        ({"amounts": [-1.0, 200.0]}, "nonnegative"),
        ({"remaining_months": [0, 24]}, "positive"),
        ({"remaining_months": [12.5, 24]}, "whole numbers"),
        ({"default_flags": [0, 2]}, "0 or 1"),
        ({"default_flags": [0.5, 1]}, "0 or 1"),
        ({"base_pd": [[0.05], [0.12]]}, "one-dimensional"),
        ({"base_pd": []}, "equal lengths"),
    ]
    for replacement, error in bad_cases:
        inputs = dict(valid, **replacement)
        with pytest.raises(ValueError, match=error):
            scenario_portfolio_ecl(**inputs)
    with pytest.raises(ValueError, match="empty portfolio"):
        scenario_portfolio_ecl([], [], [], [])
    with pytest.raises(ValueError, match="Base LGD"):
        scenario_portfolio_ecl(**valid, base_lgd=float("nan"))


def test_portfolio_ead_and_stage_counts_reconcile_exactly():
    df = scenario_portfolio_ecl(
        base_pd=[0.01, 0.1, 0.45],
        amounts=[100.0, 200.0, 300.0],
        remaining_months=[12, 24, 36],
        default_flags=[0, 0, 1],
    )
    assert np.allclose(df["portfolio_ead"], 600.0)
    assert ((df["stage1_count"] + df["stage2_count"] + df["stage3_count"]) == 3).all()
    assert (df["portfolio_ecl"] >= 0.0).all()
