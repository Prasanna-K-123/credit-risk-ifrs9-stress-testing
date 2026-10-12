from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import BASE_LGD, SCENARIOS
from src.ecl import assign_stage, compute_ead, lifetime_ecl


def stressed_pd(base_pd, multiplier: float):
    return np.clip(np.asarray(base_pd, dtype=float) * multiplier, 0, 0.999)


def scenario_portfolio_ecl(
    base_pd,
    amounts,
    remaining_months,
    default_flags,
    base_lgd: float = BASE_LGD,
) -> pd.DataFrame:
    # Fail closed: zip() would silently truncate mismatched portfolio vectors
    # while the old EAD aggregate would still include every supplied amount.
    base_pd = np.asarray(base_pd, dtype=float)
    amounts = np.asarray(amounts, dtype=float)
    remaining_months = np.asarray(remaining_months, dtype=float)
    default_flags = np.asarray(default_flags, dtype=float)
    vectors = (base_pd, amounts, remaining_months, default_flags)
    if any(v.ndim != 1 for v in vectors):
        raise ValueError("Portfolio inputs must all be one-dimensional arrays.")
    n = base_pd.size
    if n == 0:
        raise ValueError("An empty portfolio cannot produce scenario ECL.")
    if any(v.size != n for v in vectors):
        raise ValueError("PD, amount, maturity and default vectors must have equal lengths.")
    if any(not np.isfinite(v).all() for v in vectors):
        raise ValueError("Portfolio inputs must be finite.")
    if np.any((base_pd < 0) | (base_pd > 1)):
        raise ValueError("PD must be within [0, 1].")
    if np.any(amounts < 0):
        raise ValueError("Amounts must be nonnegative.")
    if np.any((remaining_months <= 0) | (remaining_months != np.floor(remaining_months))):
        raise ValueError("Remaining months must be positive whole numbers.")
    if np.any((default_flags != 0) & (default_flags != 1)):
        raise ValueError("Default flags must be 0 or 1.")
    if not np.isfinite(base_lgd) or not (0 <= base_lgd <= 1):
        raise ValueError("Base LGD must be finite and within [0, 1].")
    remaining_months = remaining_months.astype(int)
    default_flags = default_flags.astype(int)
    rows = []

    for scenario in SCENARIOS:
        pds = stressed_pd(base_pd, scenario.pd_multiplier)
        lgd = min(base_lgd + scenario.lgd_addon, 1.0)
        ecls = []
        stages = []

        for pd_i, amount_i, months_i, default_i in zip(
            pds, amounts, remaining_months, default_flags
        ):
            stage = assign_stage(pd_i, default_flag=default_i)
            ead = compute_ead(amount_i)
            ecl = lifetime_ecl(
                pd_i,
                ead,
                lgd=lgd,
                stage=stage,
                remaining_months=months_i,
            )
            stages.append(stage)
            ecls.append(ecl)

        rows.append(
            {
                "scenario": scenario.name,
                "weight": scenario.weight,
                "pd_multiplier": scenario.pd_multiplier,
                "lgd": lgd,
                "portfolio_ead": float(np.sum(amounts)),
                "portfolio_ecl": float(np.sum(ecls)),
                "weighted_ecl": float(scenario.weight * np.sum(ecls)),
                "stage1_count": int(np.sum(np.asarray(stages) == 1)),
                "stage2_count": int(np.sum(np.asarray(stages) == 2)),
                "stage3_count": int(np.sum(np.asarray(stages) == 3)),
            }
        )

    df = pd.DataFrame(rows)
    return df
