# Where earlier bank-risk models stop working

**Research release: October 10, 2026.** A registered retrospective temporal comparison used 237,253 eligible bank-year observations reconstructed from official FDIC source extracts. The final evaluation contains **57,896 observations, 6,477 certificates and 35 failures** across April 2015–April 2025 prediction anchors, with horizons ending by April 2026.

The calibrated gradient-boosting challenger has better pooled AUC, average precision, Brier and log loss than the calibrated full logistic model. That finding does **not** establish successful deployment: the frozen monitoring rule misses **nine of ten failures in the later 2022–2025 prediction cohorts**. The model underestimates their aggregate event count, and bank-cluster uncertainty does not establish an improvement in illustrative monitoring cost. Both findings are retained.

This is **institutional certificate failure**, not borrower default, empirical IFRS9 PD, or historical point-in-time performance. It extends the same credit-risk project; it does not replace the original South German or Taiwan studies.

## Why this evidence is different

Earlier loan datasets have no independent observation/outcome calendar cohorts. Repeated random splits cannot test later-period performance. [Source qualification and alternatives](FDIC_DATA_QUALIFICATION.md) compares the open FDIC route with official loan-level mortgage history requiring registration. Borrower out-of-time evidence remains an open requirement.

The [protocol](../reference/fdic_temporal/PROTOCOL.json), fitting code, metric implementation and source reconstruction were published at commit [`231a09b`](https://github.com/Prasanna-K-123/credit-risk-ifrs9-stress-testing/commit/231a09b18b7648c964a5e2e3bf5e458b8876ee74) and remotely hash-checked before model fitting or final-score inspection. A disclosed schema probe inspected two 2023 report rows and one 2000 development row, without final labels or performance statistics.

After seeing results, changes were limited to lossless compression/replay, descriptive diagnostics and documentation. No feature, split, model grid, calibration fit, policy weight, threshold-selection rule or final case was replaced. The 2022–2025 subgroup is **post hoc**, prompted by the observed annual results; it is not another untouched holdout.

## Calendar and population contract

A genuine December 31 financial report is assumed usable on the following April 1. The target interval is **(April 1, next April 1]**, a rolling one-year horizon rather than January–December. That three-month availability convention is not verified publication time. Financial values come from a current historical snapshot and can include later revisions; original-release vintages are not reconstructed.

| Partition | Report years | Prediction years | Eligible rows | Failures | Nonfailure exits |
|---|---|---|---:|---:|---:|
| Development | 1992–2005 | 1993–2006 | 148,144 | 105 | 7,143 |
| Model selection | 2007–2008 | 2008–2009 | 16,649 | 204 | 439 |
| Calibration | 2010 | 2011 | 7,561 | 82 | 182 |
| Monitoring policy | 2012 | 2013 | 7,003 | 25 | 261 |
| Final evaluation | 2014–2024 | 2015–2025 | 57,896 | 35 | 2,157 |

Report years 2006, 2009, 2011 and 2013 are purged. Each earlier partition's latest outcome horizon ends strictly before the next partition's first prediction. All final outcomes mature before the registered August 19, 2026 cutoff. Repeated certificates are intentional longitudinal observations; this does not test previously unseen institutions.

Official acquisition captured 243,449 annual financial records, 27,835 institution records and 4,117 failure/assistance records with complete pagination and unique source keys. Assistance is excluded from the failure target. After explicit eligibility exclusions, 237,253 rows and 16,219 certificates remain. The [eligibility audit](../reference/fdic_temporal/eligibility_audit.json) records every exclusion category: 2,969 inactive at prediction; 2,023 unmatched; 668 unknown establishment/insurance dates; 359 unknown inactive dates; 87 reports before establishment/insurance; 80 already failed; and 10 contradictory failure/inactive dates. Three listed failures in the 1993 prediction cohort and one in 1999 lack eligible coverage. Every listed failure in the final prediction cohorts is covered.

A merger, ordinary closure or insurance exit during the horizon is a competing nonfailure outcome. The target is not hypothetical failure without those exits. Current institution status and historical inactive/establishment/insurance dates help construct eligibility and outcomes, but are never predictors. This construction still depends on the correctness and revision history of the current institution registry.

## Models and controls

Nine fixed predictors use reported capital, loan, deposit, cash and security ratios, nonperforming assets, ROA, net interest margin and nominal log assets. Published percentage fields are converted to fractions. `NIMY` is the margin field; monetary net interest income `NIM` is not substituted. Certificates, dates, current status, failure/closure information and future macro variables are excluded from model inputs.

The constant and capital-only logistic baselines have no search. Full logistic regression searches C ∈ {0.01, 0.1, 1}; gradient boosting searches {7, 15, 31} leaves with otherwise fixed settings. Both full models use the same 148,144 development rows and three trials. Selection minimizes later selection-year log loss, choosing **C = 0.1 and seven leaves**. Imputation/scaling fit only development rows; boosting uses native missing-value routing. Neither model is refitted on later partitions.

A separate-year monotone logistic calibration maps logits with a nonnegative slope. A different year's labels select the monitoring threshold under illustrative false-negative/false-positive weights of 100:1. Those weights are not measured losses or an observed financial benefit. Separately, a fixed annual capacity diagnostic reviews the highest ceil(1% × eligible banks) scores; certificates break exact ties without entering the predictive model.

## All pooled results

Final failure prevalence is **0.06045%**. Accuracy alone would obscure the event-detection problem. Lower Brier/log loss is better; higher AUC/AP is better.

| Model | AUC | Average precision | Brier | Log loss | Monitored bank-years | Failures caught |
|---|---:|---:|---:|---:|---:|---:|
| Constant development event rate | 0.5000 | 0.00060 | 0.00060418 | 0.005093 | 0 | 0/35 |
| Capital-only logistic | 0.9189 | 0.02776 | 0.00060408 | 0.005026 | 1,470 | 20/35 |
| Full logistic, raw | 0.8381 | 0.05230 | 0.00059751 | 0.004227 | 445 | 18/35 |
| Full logistic, calibrated | 0.8381 | 0.05230 | 0.00063565 | 0.005461 | 445 | 18/35 |
| Gradient boosting, raw | 0.9155 | 0.14905 | 0.00055563 | 0.003196 | 381 | 22/35 |
| Gradient boosting, calibrated | 0.9155 | 0.14905 | 0.00055623 | 0.003231 | 381 | 22/35 |

Capital-only logistic has slightly higher pooled AUC than boosting. Calibration worsens both full models' Brier/log loss relative to their raw probabilities; calibrated logistic is also worse on those scores than the constant baseline. It predicts 166.40 aggregate failures against 35 observed, whereas calibrated boosting predicts 28.77. An aggregate predicted count is a diagnostic, not a guarantee of calibration at bank or annual level. Raw and calibrated results remain visible; the registered primary comparison is not changed to whichever version looks best.

Calibrated boosting monitors 381 bank-years, catches 22 failures and flags 359 nonfailures: precision **5.77%**, recall **62.86%**. The annual top-1% capacity diagnostic catches 23/35 across 584 reviews; this is a different rule from the frozen cost-selected threshold and includes 106 reviews in two zero-failure cohorts.

## Paired uncertainty

The registered comparison is calibrated boosting minus calibrated full logistic. Each interval uses 500 paired cluster-bootstrap replicates of fixed test predictions. All 500 replicates were valid here.

| Difference | Observed | Bank-cluster 95% interval | Annual-cohort 95% interval |
|---|---:|---|---|
| AUC | +0.07749 | [0.01846, 0.15354] | [0.03138, 0.14772] |
| Average precision | +0.09675 | [0.00947, 0.21959] | [0.01431, 0.23824] |
| Brier | −0.00007941 | [−0.00016517, −0.00001019] | [−0.00015581, −0.00001684] |
| Log loss | −0.00223028 | [−0.00268937, −0.00175688] | [−0.00282722, −0.00153543] |
| Illustrative cost per row | −0.00808346 | [−0.01812851, 0.00128873] | [−0.01380767, −0.00223477] |

The cost conclusion changes with the dependence assumption. Bank clustering allows no improvement; annual clustering does not. The two schemes are separate sensitivity analyses, with only 11 annual clusters. They do not jointly model bank and calendar dependence, refit models, include selection uncertainty, adjust for multiple comparisons, or validate point-in-time performance.

## The later failures that pooled metrics hide

| Prediction year | Rows | Failures | Boosting AUC | Boosting AP | Caught at annual top-1% capacity |
|---|---:|---:|---:|---:|---:|
| 2015 | 6,405 | 5 | 0.9884 | 0.03877 | 3/5 |
| 2016 | 6,114 | 7 | 0.9993 | 0.61698 | 7/7 |
| 2017 | 5,841 | 5 | 0.9842 | 0.28061 | 4/5 |
| 2018 | 5,597 | 0 | Undefined | Undefined | 0/0 |
| 2019 | 5,346 | 5 | 0.9942 | 0.31472 | 4/5 |
| 2020 | 5,112 | 3 | 0.9997 | 0.69841 | 3/3 |
| 2021 | 4,978 | 0 | Undefined | Undefined | 0/0 |
| 2022 | 4,794 | 2 | 0.4901 | 0.00064 | 0/2 |
| 2023 | 4,674 | 3 | 0.6843 | 0.01158 | 1/3 |
| 2024 | 4,572 | 3 | 0.8939 | 0.00462 | 0/3 |
| 2025 | 4,463 | 2 | 0.8213 | 0.50063 | 1/2 |

The post-hoc later group has 18,503 rows and ten failures. Calibrated boosting predicts 3.00 aggregate events and catches **one** under the frozen threshold, or **two** at annual top-1% capacity. Full calibrated logistic catches none under either rule despite predicting 39.18 aggregate events. The results motivate investigation of shifted event mechanisms and absent information; they do not identify a causal explanation. The frozen test cannot now certify a redesigned model.

All 35 failures, their scores and both decisions are published in [the case audit](../reference/fdic_temporal/failure_cases.csv), alongside [annual diagnostics](../reference/fdic_temporal/cohort_diagnostics.csv) and [the explicitly descriptive audit](../reference/fdic_temporal/descriptive_audit.json). No missed case is dropped or relabelled because it is inconvenient.

## Reproduction and provenance

```bash
python -m pip install -r requirements-fdic-temporal.txt
python -m pytest -q
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python replay_fdic_temporal.py
```

The release commits 31 lossless compact original-source extracts, acquisition indices/counts/hashes, eligibility rules, the pre-fit protocol, all selection trials, six full-model prediction columns, annual diagnostics and all failure cases. The 10,432,670-byte prediction CSV is committed as gzip and restored with its exact first-evaluation SHA-256; an existing altered CSV is rejected. Replay checks release hashes, rebuilds every predictor/label/eligibility decision, fits the registered candidates, and verifies all frozen probabilities, monitoring counts, metrics and dependence intervals. The first local replay had maximum probability error **0.0**. CI uses the same restoration and strict replay path, without live FDIC requests.

Source indices: financial `risview_20260819185831`, institutions `institutions_20261009090008`, failures `failures_1787667198788`. [The snapshot receipt](../reference/fdic_temporal/source_snapshot.json) retains exact queries, pagination and source metadata. Original response envelopes and official schemas are not redistributed; compact selected source objects retain their original types/nulls and values. Source attribution remains FDIC, with no FDIC endorsement or invented source licence.

The evidence strengthens calendar separation, source lineage, rare-event evaluation and model-risk judgement. It does not close borrower-level dated validation, original-vintage availability, prospective validation, production IFRS9 approval, or independent external review. Candidate ownership and interview mastery remain separate assessments.
