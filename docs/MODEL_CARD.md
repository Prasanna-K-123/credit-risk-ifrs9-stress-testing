# PD scorecard model card

## Intended use

Educational/research demonstration of a traditional application-style credit scorecard, model validation, challenger comparison and integration into an IFRS 9-style ECL engine.

## Primary model

A logistic regression fitted to Weight-of-Evidence transformed predictors. Continuous variables are binned from training-sample quantiles; categorical mappings and WoE statistics are learned on the training sample only. The target is inverted from UCI's `credit_risk` coding so `default=1` represents a bad credit outcome.

## Challenger

Random forest with one-hot encoding for coded categorical features. It is used as a non-linear benchmark, not automatically promoted over the primary model.

## Validation

The pipeline reports ROC-AUC, Gini, KS, Brier score, calibration intercept/slope, 95% bootstrap AUC interval, asymmetric misclassification cost and PSI. Because the dataset contains no dates, the holdout is a stratified random holdout, **not** an out-of-time sample.

## Prohibited interpretation

The outputs are not production approval scores, accounting provisions, regulatory capital estimates, or institution-specific IFRS 9 parameters.
