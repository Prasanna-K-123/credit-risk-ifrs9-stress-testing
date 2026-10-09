"""Paired uncertainty, frozen lending policy and assumed prevalence-shift audit.

No model is refit on the already-published holdout. Prior-shift scenarios assume
unchanged class-conditional features and are not measured deployment performance.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.metrics import roc_auc_score, brier_score_loss

ROOT = Path(__file__).resolve().parent


def prior_adjust(p, source_prior, target_prior):
    if not 0 < source_prior < 1 or not 0 < target_prior < 1:
        raise ValueError('Priors must lie strictly inside (0,1)')
    p = np.asarray(p, dtype=float)
    if np.any(~np.isfinite(p)) or np.any((p<=0)|(p>=1)):
        raise ValueError('Predictions must lie strictly inside (0,1)')
    return expit(logit(p)+logit(target_prior)-logit(source_prior))


def paired_intervals(y, p, q, repetitions=2000, seed=20261009):
    rng = np.random.default_rng(seed)
    differences = []
    for _ in range(repetitions):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            continue
        differences.append([roc_auc_score(y[idx],q[idx])-roc_auc_score(y[idx],p[idx]),
                            brier_score_loss(y[idx],q[idx])-brier_score_loss(y[idx],p[idx])])
    return np.quantile(differences, [.025,.975], axis=0)


def main():
    source = ROOT/'outputs/holdout_predictions.csv'
    frame = pd.read_csv(source)
    y = frame.observed_default.to_numpy(dtype=int)
    p, q = frame.pd_scorecard.to_numpy(), frame.pd_challenger.to_numpy()
    if len(y) != 200 or y.sum() != 60:
        raise ValueError('Frozen holdout identity/count changed')
    intervals = paired_intervals(y,p,q)
    original = json.loads((ROOT/'outputs/metrics.json').read_text())
    threshold = original['cost_sensitive_threshold']['threshold']
    accepted = p < threshold
    fn, fp = int(np.sum(accepted&(y==1))), int(np.sum(~accepted&(y==0)))
    out = ROOT/'outputs/decision_audit'
    out.mkdir(parents=True, exist_ok=True)
    summary = dict(holdout_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), rows=len(y),
                   auc_challenger_minus_scorecard=float(roc_auc_score(y,q)-roc_auc_score(y,p)),
                   paired_auc_difference_ci95=intervals[:,0].tolist(),
                   brier_challenger_minus_scorecard=float(brier_score_loss(y,q)-brier_score_loss(y,p)),
                   paired_brier_difference_ci95=intervals[:,1].tolist(),
                   frozen_validation_threshold=threshold, holdout_false_negatives=fn,
                   holdout_false_positives=fp, holdout_weighted_cost_5_to_1=5*fn+fp,
                   approve_all_weighted_cost=5*int(y.sum()), reject_all_weighted_cost=int((y==0).sum()),
                   warnings=['Holdout already published; this is a retrospective audit.',
                             'Challenger trained on 800 rows versus 600 for the scorecard.',
                             'No observation dates, representative deployment prior, empirical LGD or EAD.'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    rows=[]
    for prior in [.05,.10,.20,.30]:
        adjusted=prior_adjust(p,.30,prior)
        weights=np.where(y==1,prior/.30,(1-prior)/.70)
        for use_adjustment, forecast in [(False,p),(True,adjusted)]:
            reject=forecast >= 1/6  # Bayes boundary for illustrative 5:1 costs.
            weighted_cost=np.average(5*((~reject)&(y==1))+((reject)&(y==0)),weights=weights)
            rows.append(dict(assumed_target_prior=prior, prior_adjusted=use_adjustment,
                             weighted_brier=float(np.average((forecast-y)**2,weights=weights)),
                             weighted_cost_per_account=float(weighted_cost),
                             assumed_acceptance_rate=float(np.average(~reject,weights=weights))))
    pd.DataFrame(rows).to_csv(out/'prior_shift_scenarios.csv',index=False)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
