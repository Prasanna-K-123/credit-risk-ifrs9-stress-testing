"""Opt-in mathematical ECL reference; NOT wired into historical IFRS9 pipeline.

This is a constant-hazard, fixed-EAD, fixed-LGD, continuous-default-time
educational calculation. Not a production IFRS 9 valuation or a replacement
for any saved empirical FDIC/credit reference. The original lifetime_ecl()
is intentionally untouched.
"""
from __future__ import annotations

import math
from numbers import Integral, Real


def maturity_respecting_ecl_reference(
    pd_12m: float,
    ead: float,
    lgd: float,
    stage: int,
    remaining_months: int,
    effective_interest_rate: float,
) -> float:
    """Expected discounted default loss before the contractual horizon.

    Assumptions: default arrival has a constant annual hazard h=-log(1-PD12m),
    default loss equals EAD*LGD at event time, EAD and LGD are constant, and
    one year's continuous-time discount factor is 1/(1+r), where r>=0.
    Stage 1 truncates its integral at min(remaining horizon, 12 months).
    Stage 2 uses the full positive remaining horizon. Stage 3 is refused.
    The expectation is EAD*LGD * integral_0^T h*exp(-h*t)/(1+r)^t dt.

    The source historical function rounds maturities up to whole years and
    preserves a different convention. This opt-in alternative does not alter
    it or its stored numbers; no general IFRS 9 compliance is claimed.
    """
    if type(stage) is not int or stage not in (1, 2):
        raise ValueError("Only stages 1 and 2 are supported; Stage 3 needs a separate credit-impaired cash-flow model.")
    if isinstance(remaining_months, bool) or not isinstance(remaining_months, Integral) or remaining_months <= 0:
        raise ValueError("remaining_months must be a positive integer")
    inputs = (pd_12m, ead, lgd, effective_interest_rate)
    if any(isinstance(x, bool) or not isinstance(x, Real) for x in inputs):
        raise ValueError("PD, EAD, LGD and effective interest rate must be finite real numbers")
    try:
        p, exposure, severity, rate = (float(x) for x in inputs)
    except (OverflowError, ValueError) as exc:
        raise ValueError("PD, EAD, LGD and effective interest rate must be finite real numbers") from exc
    if not all(math.isfinite(x) for x in (p, exposure, severity, rate)):
        raise ValueError("PD, EAD, LGD and effective interest rate must be finite real numbers")
    if not 0.0 <= p <= 1.0:
        raise ValueError("pd_12m must lie in [0,1]")
    if not exposure >= 0:
        raise ValueError("ead must be nonnegative")
    if not 0 <= severity <= 1:
        raise ValueError("lgd must lie in [0,1]")
    if rate < 0:
        raise ValueError("nonnegative effective_interest_rate required for this bounded reference")
    # Cap Stage 1 while the term is still an integer, before float conversion.
    # Stage 2 refuses terms outside finite floating-point representation.
    months = min(remaining_months, 12) if stage == 1 else remaining_months
    try:
        horizon_years = months / 12.0
    except OverflowError as exc:
        raise ValueError("remaining_months must produce a finite horizon") from exc
    if not math.isfinite(horizon_years):
        raise ValueError("remaining_months must produce a finite horizon")
    if p == 0.0 or exposure == 0.0 or severity == 0.0:
        return 0.0
    if p == 1.0:
        return exposure * severity  # immediate-event limit as hazard -> infinity
    hazard = -math.log1p(-p)
    discount_force = math.log1p(rate)
    total_rate = hazard + discount_force
    # -expm1(-x) avoids catastrophic cancellation for small hazard/months.
    expected_loss_fraction = hazard / total_rate * (-math.expm1(-total_rate * horizon_years))
    return exposure * severity * expected_loss_fraction
