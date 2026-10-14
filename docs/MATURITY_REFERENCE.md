# Maturity-respecting loss reference

14 October 2026 · Separate mathematical reference, developed with AI assistance.

`src.maturity_reference.maturity_respecting_ecl_reference` makes the default-event horizon explicit in months. It implements the mathematical specification prepared on 12 October, with additional checks for unrepresentable numbers and durations. The historical [`lifetime_ecl`](../src/ecl.py) engine and its frozen credit, card-client and FDIC evidence retain their original conventions. The [historical maturity limitation](IFRS9_METHODOLOGY.md) remains applicable to that engine.

## Question and model

For a fixed exposure and loss severity, what is the discounted expected loss from default events occurring before the remaining maturity, without rounding the term up to whole years?

Assume a 12-month default probability `p`, constant annual hazard `h = -log(1-p)`, fixed `EAD`, fixed `LGD`, loss realized immediately at default and a nonnegative annual effective discount rate `r`. Default time has density `h exp(-h t)`. Set `T = remaining_months / 12` for Stage 2 and `T = min(1, remaining_months / 12)` for Stage 1. Then

```text
k = h + log(1+r)
ECL = EAD × LGD × integral from 0 to T of h exp(-k t) dt
    = EAD × LGD × (h/k) × (1 - exp(-k T))
```

The implementation uses `log1p` and `expm1` to retain precision near zero. Probability zero gives zero loss; probability one uses the immediate-default limit `EAD × LGD`. Stage 3 is refused because impaired-asset recovery cash flows need a separate model.

Stage 1 bounds **default-event timing**. It does not imply that cash shortfalls must fall inside one year. The IFRS Foundation's [project summary, pages 17–19](https://www.ifrs.org/-/media/project/fi-impairment/ifrs-standard/published-documents/project-summary-july-2014.pdf) distinguishes loss arising from possible defaults within twelve months from cash shortfalls confined to those months. Here, fixed LGD and immediate loss are explicit simplifying assumptions.

## Use

From the repository root:

```python
from src.maturity_reference import maturity_respecting_ecl_reference

loss = maturity_respecting_ecl_reference(
    pd_12m=0.08,
    ead=100.0,
    lgd=0.45,
    stage=2,
    remaining_months=18,
    effective_interest_rate=0.05,
)
```

Supply finite real amounts and probabilities, `0 <= p, LGD <= 1`, nonnegative EAD/rate, Stage 1 or 2, and a positive integer term. Booleans, invalid stages and nonpositive/fractional terms are refused. Stage 1 caps very large integer terms before conversion; Stage 2 refuses an unrepresentable floating-point horizon. Overflowing integer scalar inputs produce a domain error. Validation also applies when the resulting loss would be zero.

## Verification and release

The recovered 68 pytest cases remain in [`tests/test_maturity_reference.py`](../tests/test_maturity_reference.py), with 13 added numeric-boundary cases. They compare 45 survival identities, fractional-month and staging behavior, independent numerical quadrature, endpoint probabilities, monotonicity, loss bounds and domain refusals. Run:

```bash
python -m pytest -q tests/test_maturity_reference.py
python -m pytest -q
```

The repository's three existing workflows run the complete tests and their original UCI, matched-cohort and FDIC verification paths. Their exact run/commit records determine release status. Passing mathematical tests is separate from empirical PD/LGD calibration. The historical sources and reference files must remain unchanged during integration.

## Interpretation boundary

This scalar reference excludes amortization, changing exposure or severity, macroeconomic conditioning, prepayment, delayed recoveries, origination PD, SICR assessment and contractual effective-interest mechanics. It is an educational constant-hazard calculation, not an accounting-compliant provision, a production migration or borrower-level empirical validation. Historical adverse findings and research limits remain part of the evidence.
