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
