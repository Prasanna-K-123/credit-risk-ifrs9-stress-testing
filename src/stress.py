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
    rows = []
    base_pd = np.asarray(base_pd, dtype=float)
    amounts = np.asarray(amounts, dtype=float)
    remaining_months = np.asarray(remaining_months, dtype=int)
    default_flags = np.asarray(default_flags, dtype=int)

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
