from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src.data import development_split, load_south_german_credit
from src.pd_model import ScorecardModel, fit_challenger
from src.reporting import (
    ensure_dirs,
    plot_calibration,
    plot_pd_distribution,
    plot_roc,
    save_json,
    write_validation_report,
)
from src.stress import scenario_portfolio_ecl
from src.validation import (
    bootstrap_auc_ci,
    cost_sensitive_threshold,
    discrimination_and_calibration,
    grade_distribution,
    population_stability_index,
)


def main() -> None:
    ensure_dirs()
    X, y = load_south_german_credit()

    if len(X) != 1000:
        raise RuntimeError(f"Expected 1,000 UCI rows, received {len(X)}")
    if int(y.sum()) != 300:
        raise RuntimeError(f"Expected 300 bad/default observations, received {int(y.sum())}")
    if X.isna().any().any():
        raise RuntimeError("Unexpected missing values in UCI source data.")

    X_train, X_val, X_test, y_train, y_val, y_test = development_split(X, y)

    scorecard = ScorecardModel.fit(X_train, y_train)
    val_pd = scorecard.predict_proba(X_val)
    test_pd = scorecard.predict_proba(X_test)
    train_pd = scorecard.predict_proba(X_train)

    challenger = fit_challenger(pd.concat([X_train, X_val]), pd.concat([y_train, y_val]))
    challenger_test_pd = challenger.predict_proba(X_test)[:, 1]

    val_metrics = discrimination_and_calibration(y_val, val_pd)
    test_metrics = discrimination_and_calibration(y_test, test_pd)
    ci = bootstrap_auc_ci(y_test, test_pd, n_boot=1500)
    test_metrics["auc_ci_95"] = [ci[0], ci[1]]
    challenger_metrics = discrimination_and_calibration(y_test, challenger_test_pd)

    threshold = cost_sensitive_threshold(y_val, val_pd)
    psi = population_stability_index(
        np.concatenate([train_pd, val_pd]),
        test_pd,
    )

    scorecard_features = scorecard.coefficient_table()
    scorecard_features.to_csv("outputs/scorecard_feature_summary.csv", index=False)

    predictions = X_test[["duration", "amount", "age"]].copy()
    predictions["observed_default"] = y_test.astype(int).values
    predictions["pd_scorecard"] = test_pd
    predictions["pd_challenger"] = challenger_test_pd
    predictions.to_csv("outputs/holdout_predictions.csv", index=False)

    stress_summary = scenario_portfolio_ecl(
        base_pd=test_pd,
        amounts=X_test["amount"].to_numpy(),
        remaining_months=X_test["duration"].to_numpy(),
        default_flags=y_test.to_numpy(),
    )
    stress_summary.to_csv("outputs/stress_ecl_summary.csv", index=False)

    scenario_weighted_ecl = float(stress_summary["weighted_ecl"].sum())
    portfolio_ead = float(stress_summary["portfolio_ead"].iloc[0])

    metrics = {
        "data": {
            "rows": int(len(X)),
            "features": int(X.shape[1]),
            "default_count": int(y.sum()),
            "default_rate": float(y.mean()),
            "train_rows": int(len(X_train)),
            "validation_rows": int(len(X_val)),
            "test_rows": int(len(X_test)),
        },
        "scorecard_validation": val_metrics,
        "scorecard_test": test_metrics,
        "challenger_test": challenger_metrics,
        "cost_sensitive_threshold": threshold,
        "holdout_psi": float(psi),
        "grade_distribution_test": grade_distribution(test_pd),
        "scenario_weighted_ecl": scenario_weighted_ecl,
        "portfolio_ead_holdout": portfolio_ead,
        "scenario_weighted_ecl_rate": float(scenario_weighted_ecl / portfolio_ead),
        "methodology_flags": {
            "genuine_out_of_time_validation": False,
            "empirical_lgd_model": False,
            "empirical_ead_model": False,
            "ifrs9_scenario_parameters": "illustrative",
            "ead_demo_proxy": "observed credit amount",
        },
    }
    save_json(metrics, "outputs/metrics.json")

    plot_roc(y_test, test_pd, "reports/generated/roc_curve.png")
    plot_calibration(y_test, test_pd, "reports/generated/calibration_curve.png")
    plot_pd_distribution(y_test, test_pd, "reports/generated/pd_distribution.png")
    write_validation_report(
        metrics,
        scorecard_features,
        stress_summary,
        "reports/generated/model_validation_report.md",
    )

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
