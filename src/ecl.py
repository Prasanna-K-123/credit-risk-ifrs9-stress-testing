from __future__ import annotations

import numpy as np

from src.config import (
    BASE_LGD,
    EFFECTIVE_INTEREST_RATE,
    SICR_RATIO,
    STAGE2_ABSOLUTE_PD,
)


def compute_ead(drawn: float, undrawn: float = 0.0, ccf: float = 0.75) -> float:
    if drawn < 0 or undrawn < 0:
        raise ValueError("Exposures must be non-negative.")
    if not 0 <= ccf <= 1:
        raise ValueError("CCF must be in [0, 1].")
    return float(drawn + ccf * undrawn)


def assign_stage(
    current_pd: float,
    default_flag: int = 0,
    origination_pd: float | None = None,
    sicr_ratio: float = SICR_RATIO,
    absolute_stage2_pd: float = STAGE2_ABSOLUTE_PD,
) -> int:
    """Illustrative IFRS 9 staging logic.

    If an origination PD is available, SICR is tested using a PD ratio.
    Otherwise an explicitly documented absolute-PD fallback is used.
    Observed default is used as a Stage 3 proxy in this retrospective demo.
    """
    current_pd = float(np.clip(current_pd, 0.0, 1.0))
    if int(default_flag) == 1:
        return 3
    if origination_pd is not None and origination_pd > 0:
        if current_pd / origination_pd >= sicr_ratio:
            return 2
    elif current_pd >= absolute_stage2_pd:
        return 2
    return 1


def annual_hazard_from_pd(pd_12m: float) -> float:
    pd_12m = float(np.clip(pd_12m, 1e-9, 1 - 1e-9))
    return float(-np.log(1 - pd_12m))


def lifetime_ecl(
    pd_12m: float,
    ead: float,
    lgd: float = BASE_LGD,
    stage: int = 1,
    remaining_months: int = 12,
    effective_interest_rate: float = EFFECTIVE_INTEREST_RATE,
) -> float:
    pd_12m = float(np.clip(pd_12m, 0, 1))
    lgd = float(np.clip(lgd, 0, 1))
    ead = max(float(ead), 0.0)

    if stage == 3:
        return ead * lgd
    if stage == 1:
        return pd_12m * lgd * ead
    if stage != 2:
        raise ValueError("stage must be 1, 2 or 3")

    years = max(int(np.ceil(max(remaining_months, 1) / 12)), 1)
    hazard = annual_hazard_from_pd(pd_12m)
    survival = 1.0
    ecl = 0.0

    for year in range(1, years + 1):
        conditional_pd = 1 - np.exp(-hazard)
        marginal_pd = survival * conditional_pd
        discount = (1 + effective_interest_rate) ** year
        ecl += marginal_pd * lgd * ead / discount
        survival *= 1 - conditional_pd

    return float(ecl)
