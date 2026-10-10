# Governance, limitations and validation standards

## Scope of the dated FDIC extension

The separate [registered FDIC comparison](FDIC_TEMPORAL_REVIEW.md) provides retrospective calendar-separated institutional-failure evidence. It does not turn the UCI borrower studies into dated samples, establish original-release information availability, or calibrate an IFRS9 provision. Its later-period failures, calibration deterioration, competing exits, rare outcomes and dependence-sensitive monitoring-cost conclusion are retained. The borrower-specific limitations below continue to apply to the original study.

## Model-risk principles implemented

1. **Source traceability** — public UCI source and DOI are documented.
2. **Leakage control** — WoE bins and mappings are fitted on training data only.
3. **Primary/challenger architecture** — interpretable scorecard benchmarked against a non-linear challenger.
4. **Multiple validation dimensions** — discrimination, calibration, uncertainty, cost-sensitive decisions and stability.
5. **Assumption transparency** — LGD, EAD proxy, scenario weights and stress severities are identified as illustrative.
6. **Reproducibility** — deterministic seeds, tests and CI regenerate the evidence.
7. **No false OOT claim** — absence of dates is explicitly disclosed.

## Material limitations

- only 1,000 observations;
- 1970s-era credit population and outdated feature context;
- bad-credit oversampling affects population calibration;
- random holdout rather than temporal validation;
- no recovery/utilisation data for empirical LGD/EAD;
- no macroeconomic linkage model;
- no institution-specific policy, default definition, cure logic or overrides;
- no fairness/compliance approval for production use.

## Production validation plan

A production-grade validation would require independent data lineage checks, representative development and OOT samples, segmentation review, recalibration to current portfolio default rates, benchmark/challenger analysis, calibration tests by risk band, vintage analysis, override analysis, stability monitoring, stress testing, documented model-change controls, issue tracking and periodic independent validation.
