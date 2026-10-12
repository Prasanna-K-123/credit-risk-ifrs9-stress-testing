# IFRS 9-style ECL methodology

This module demonstrates the mechanics that connect PD, LGD, EAD, staging and forward-looking scenarios. It deliberately separates **implemented mechanics** from **empirical estimation**.

## Staging

`assign_stage()` supports:

- Stage 3 when a default flag is present;
- Stage 2 via a current-PD/origination-PD SICR ratio when origination PD is available;
- a documented absolute-PD fallback when origination PD is unavailable;
- Stage 1 otherwise.

The UCI demonstration has no origination/current longitudinal PD pair, so the fallback is used. That is a data limitation, not presented as an IFRS 9 policy recommendation.

## PD

The empirical component is the scorecard's one-period probability of bad/default outcome.

For Stage 2, the current implementation converts a clipped 12-month PD to a constant annual hazard and sums **full-year** marginal default probabilities over `max(ceil(max(remaining_months, 1) / 12), 1)` years, discounted at each year end. This is an **annual-ceiling approximation**, not exact remaining contractual-horizon integration: 1 and 12 months produce the same duration, as do 13 and 24 months. A zero or negative maturity is coerced to **one full year**, rather than being rejected or producing zero remaining payments. Stage 1 ignores `remaining_months` altogether and applies a complete 12-month PD; Stage 3 applies full LGD×EAD without a term calculation. The source does not validate shortened-horizon treatment of near-maturity assets. These behaviors are explicitly preserved for historical reproduction, not endorsed as accurate IFRS 9 measurement. A production-grade implementation would need specified maturity/contract policies and calibrated marginal PD term structures rather than silently rounding up.

## LGD

The demo starts from 45% LGD and applies scenario add-ons. These are **illustrative assumptions**, not empirical estimates. The UCI data contain no recovery cash flows.

## EAD

The engine supports drawn exposure plus CCF × undrawn amount. The demonstration uses the dataset's credit amount as a drawn-exposure proxy and zero undrawn exposure because utilisation histories are unavailable.

## Forward-looking scenarios

The repository uses base/downside/severe scenarios with explicit weights and PD/LGD shocks. These are transparent stress assumptions for architecture demonstration only. Production IFRS 9 requires governance-approved, probability-weighted macroeconomic scenarios and defensible links from macro factors to risk parameters.

## Discounting

Stage 2 ECL is discounted using an illustrative 5% effective interest rate because contractual EIR is absent from the source data.
