from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import RocCurveDisplay


def ensure_dirs() -> None:
    for path in ["outputs", "reports/generated"]:
        Path(path).mkdir(parents=True, exist_ok=True)


def save_json(data: dict, path: str) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def plot_roc(y_true, pd_hat, path: str) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    RocCurveDisplay.from_predictions(y_true, pd_hat, ax=ax)
    ax.set_title("Holdout ROC curve — PD scorecard")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_calibration(y_true, pd_hat, path: str) -> None:
    prob_true, prob_pred = calibration_curve(y_true, pd_hat, n_bins=8, strategy="quantile")
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.plot(prob_pred, prob_true, marker="o", label="Observed")
    ax.plot([0, 1], [0, 1], linestyle="--", label="Perfect calibration")
    ax.set_xlabel("Predicted probability of default")
    ax.set_ylabel("Observed default frequency")
    ax.set_title("Holdout calibration")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_pd_distribution(y_true, pd_hat, path: str) -> None:
    y_true = np.asarray(y_true)
    pd_hat = np.asarray(pd_hat)
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.hist(pd_hat[y_true == 0], bins=20, alpha=0.55, label="Good / non-default")
    ax.hist(pd_hat[y_true == 1], bins=20, alpha=0.55, label="Bad / default")
    ax.set_xlabel("Predicted probability of default")
    ax.set_ylabel("Count")
    ax.set_title("PD score separation on holdout")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def write_validation_report(
    metrics: dict,
    scorecard_features: pd.DataFrame,
    stress_summary: pd.DataFrame,
    path: str,
) -> None:
    m = metrics["scorecard_test"]
    challenger = metrics["challenger_test"]
    cost = metrics["cost_sensitive_threshold"]
    psi = metrics["holdout_psi"]

    top_features = scorecard_features.head(10).to_markdown(index=False)
    stress = stress_summary.to_markdown(index=False)

    report = f"""# Independent-style model validation report

## Executive conclusion

This repository demonstrates a compact credit-risk development and validation workflow on the UCI South German Credit dataset. The primary model is an interpretable WoE logistic scorecard; a random-forest model is retained as a non-linear challenger.

**Holdout performance:** ROC-AUC {m['auc']:.3f}, Gini {m['gini']:.3f}, KS {m['ks']:.3f}, Brier score {m['brier']:.3f}. The 95% bootstrap interval for holdout AUC is {m['auc_ci_95'][0]:.3f}–{m['auc_ci_95'][1]:.3f}. The challenger holdout AUC is {challenger['auc']:.3f}.

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

The cost-sensitive validation threshold is **{cost['threshold']:.3f}**, producing weighted misclassification cost **{cost['weighted_cost']:.0f}** under the illustrative 5:1 false-negative / false-positive cost ratio.

Holdout PSI versus the development sample is **{psi:.4f}**. Because the dataset has no timestamps, this is a random-sample stability diagnostic and **must not be interpreted as temporal drift or out-of-time validation**.

## Highest-IV scorecard variables

{top_features}

## Stress and ECL summary

{stress}

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
"""
    Path(path).write_text(report, encoding="utf-8")
