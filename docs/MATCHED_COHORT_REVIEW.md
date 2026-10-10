# Equal-budget credit validation: Taiwan card-client cohort

Frozen protocol before fitting: [PROTOCOL.json](../reference/card_clients/PROTOCOL.json). This extends, and does not overwrite, the earlier corrected South German credit study.

## Question and data

Does a nonlinear challenger add predictive or decision value once both models have the **same training and calibration budgets**? Official UCI dataset: [I-Cheng Yeh, Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients), DOI 10.24432/C55S3H, **CC BY 4.0**. Source XLS SHA256 `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933`. Public predictors include April–September2005 payment/bill history and a next-month binary default label. This is one client cohort, **not a time series of independent lending vintages**.

30,000 records; 20 identical predictors per model. ID, sex, education and marital status are excluded from fitting. Age remains a predictor. Exclusion alone does not establish fairness. There are **231 repeated model-input rows**: all duplicate vectors stay together across the four partitions, including any discordant outcomes. Model-input hashes are grouping devices, not verified person IDs.

| Partition | Rows | Unique input groups | Defaults |
|---|---:|---:|---:|
| train | 18,007 | 17,861 | 3,964 |
| calibration | 2,992 | 2,977 | 680 |
| policy_validation | 3,000 | 2,977 | 697 |
| test | 6,001 | 5,954 | 1,295 |

## Prespecified models and decisions

Five-quantile, training-only WoE + logistic regression versus histogram gradient boosting (200 iterations,31 leaves, learning rate0.05, L2=10, no early stopping). No test-driven tuning or automated feature/model search. Both fit **18,007 identical training clients**, calibrate on **2,992**, select a threshold on **3,000**, and score **6,001** untouched test clients.

Separate regularized logistic calibration operates on clipped log odds. Thresholds minimize policy-validation cost over0.01–0.99: false-negative weight5 and false-positive weight1. These are assumed error weights, **not measured losses, currency, utility or actual approve/reject policies**. The calibration fits were not selected based on the test; raw test Brier scores are retained because calibration can worsen generalization.

| Holdout measure | WoE/logistic | Gradient-boosting challenger |
|---|---:|---:|
| auc | 0.781429 | 0.789673 |
| brier | 0.130794 | 0.130042 |
| raw_test_brier | 0.130485 | 0.129523 |
| log_loss | 0.421723 | 0.417471 |
| threshold | 0.150000 | 0.210000 |
| false_negative | 233 | 422 |
| false_positive | 2,157 | 1,177 |
| accepted | 2,782 | 3,951 |
| cost_units | 3,322 | 3,287 |

## What the comparison supports

- Challenger-minus-scorecard auc: **0.008243**, nominal 95% paired group-bootstrap interval **[0.000555,0.016102]**.
- Challenger-minus-scorecard brier: **-0.000752**, nominal 95% paired group-bootstrap interval **[-0.002191,0.000646]**.
- Challenger-minus-scorecard cost_per_client: **-0.005832**, nominal 95% paired group-bootstrap interval **[-0.032834,0.019433]**.

The small AUC advantage has a positive nominal interval. The Brier and cost intervals include zero, so **a general calibration/decision superiority claim is unsupported**. Intervals are unadjusted for multiple measures and conditional on the fitted models, calibration and thresholds. They do not include training/refit uncertainty. Two thousand test input-group bootstrap draws preserve duplicate-vector members.

Calibration worsens both models' Brier scores versus their raw probabilities on this test. That adverse finding remains exposed. Accept-all costs6,475 and reject-all4,706 assumed units; selected scorecard3,322 and challenger3,287. The challenger has more missed defaults at its selected threshold, balanced against fewer false positives under the assumed weights. A different cost ratio can change the decision.

## Inspect and reproduce

- [Frozen summary](../reference/card_clients/summary.json)
- [Complete partition manifest](../reference/card_clients/partition_manifest.csv)
- [Every holdout prediction](../reference/card_clients/holdout_predictions.csv)
- [Calibration bins](../reference/card_clients/calibration_bins.csv)
- [Sex/age diagnostic slices](../reference/card_clients/group_audit.csv): descriptive comparisons, not causal discrimination findings or a fairness certificate
- [Executable benchmark](../benchmark_card_clients.py) and [workflow](../.github/workflows/card_clients.yml)

```bash
python -m pip install -r requirements-card-clients.txt
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m pytest -q
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python benchmark_card_clients.py --download --verify
```

The verification command refits both prespecified models, requires the identical partition manifest and exact decision counts, and checks model metrics within1e-7. It does not merely reread summary scores. Local reproduction passed, with all17 project tests passing. Remote CI state must be read from the actual release rather than inferred from local success.

## Interpretation limits

A group-held-out split on a single historical Taiwan cohort is **not out-of-time, multiyear, India-specific or through-cycle validation**. Existing card holders introduce selection limits; loan applicants and rejected applicants are not observed. Dates on monthly predictors do not provide independently dated lending vintages. No actual LGD/EAD, causal lending effect, current policy compliance or IFRS9 validation is established. Source data are fetched from UCI rather than redistributed in this repository; the licence/attribution above applies to the source and derived reference artifacts. Code and study preparation used AI assistance.
