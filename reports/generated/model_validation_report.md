# Independent-style model validation report

## Executive conclusion

This repository demonstrates a compact credit-risk development and validation workflow on the UCI South German Credit dataset. The primary model is an interpretable WoE logistic scorecard; a random-forest model is retained as a non-linear challenger.

**Holdout performance:** ROC-AUC 0.730, Gini 0.459, KS 0.374, Brier score 0.184. The 95% bootstrap interval for holdout AUC is 0.651–0.806. The challenger holdout AUC is 0.753.

## Validation scope

- data-quality and target checks;
- leakage-controlled train / validation / holdout split;
- WoE / IV scorecard construction;
- discrimination and calibration assessment;
- bootstrap uncertainty for AUC;
- asymmetric classification-cost threshold selection;
- population-stability check across random development and holdout samples;
- challenger benchmarking;
- rating-grade mapping;
- IFRS 9-style staging and ECL mechanics;
- multi-scenario PD/LGD stress testing;
- explicit limitations and model-risk governance notes.

## Quantitative findings

The cost-sensitive validation threshold is **0.170**, producing weighted misclassification cost **93** under the illustrative 5:1 false-negative / false-positive cost ratio.

Holdout PSI versus the development sample is **0.0392**. Because the dataset has no timestamps, this is a random-sample stability diagnostic and **must not be interpreted as temporal drift or out-of-time validation**.

## Highest-IV scorecard variables

| feature             |   coefficient |   information_value |
|:--------------------|--------------:|--------------------:|
| status              |      0.763431 |            0.652646 |
| credit_history      |      0.655981 |            0.31547  |
| duration            |      0.847268 |            0.253681 |
| savings             |      0.882629 |            0.205159 |
| purpose             |      1.17118  |            0.191109 |
| amount              |      0.763196 |            0.152901 |
| property            |      0.59556  |            0.116628 |
| age                 |      0.374003 |            0.103759 |
| housing             |      0.494198 |            0.102234 |
| employment_duration |      0.433414 |            0.101212 |

## Stress and ECL summary

| scenario   |   weight |   pd_multiplier |   lgd |   portfolio_ead |   portfolio_ecl |   weighted_ecl |   stage1_count |   stage2_count |   stage3_count |
|:-----------|---------:|----------------:|------:|----------------:|----------------:|---------------:|---------------:|---------------:|---------------:|
| base       |      0.6 |            1    |  0.45 |          674042 |          188645 |       113187   |             42 |             98 |             60 |
| downside   |      0.3 |            1.35 |  0.5  |          674042 |          226562 |        67968.6 |             32 |            108 |             60 |
| severe     |      0.1 |            1.75 |  0.6  |          674042 |          288667 |        28866.7 |             25 |            115 |             60 |

## Model-risk judgement

The exercise is suitable as a transparent demonstration of scorecard development, validation and ECL architecture. It is **not** suitable for production credit approval or accounting provisioning because the source dataset is small, historical, non-current, oversamples bad credits, contains no observation dates, no recovery cash flows, no undrawn commitments, no contractual effective interest rates and no macroeconomic time series.

LGD, scenario severity and macro weights are therefore explicitly **illustrative assumptions**, while EAD in the demo uses the observed credit amount as a drawn-exposure proxy. No claim is made that LGD or EAD were empirically estimated from this dataset.

## Required production remediation

1. replace the demonstration sample with institution-specific, current and representative development data;
2. establish genuine observation / performance windows and out-of-time validation;
3. develop segment-specific PD, LGD and EAD models from observed default, recovery and utilisation histories;
4. calibrate IFRS 9 forward-looking scenarios to defensible macroeconomic forecasts;
5. validate SICR definitions, cure/default definitions, discounting and staging against accounting policy;
6. define model inventory, ownership, approval, monitoring thresholds, overrides and independent validation cadence.
