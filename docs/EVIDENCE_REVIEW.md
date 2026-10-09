# Evidence review: Credit Risk & Lending Decisions

Independent portfolio research. Updated 2026-10-09. Development and documentation include AI assistance; the committed executable code, data provenance and test outputs establish the work products. No institutional endorsement or third-party authorship review is claimed.

## Research purpose

Financial ML, credit risk and model validation.

## Published evidence

1,000 corrected UCI observations; 200-row holdout; paired model uncertainty and a frozen lending-policy audit.

## Interpretation boundary

Small historical oversampled dataset, no observation dates; IFRS 9/LGD/EAD assumptions are illustrative.

## Review standard

Check the source data and split before interpreting a score. Compare the strongest result with a simple baseline. Inspect failed diagnostics and uncertainty. Reproduce the calculations from the documented environment; distinguish measured findings from simulated or assumed scenarios. The tests cover specific documented invariants and do not establish complete production correctness.

## Next research extension

Add a larger dated lending dataset and a locked forward evaluation. Compare equally trained baselines, calibration under a known deployment prior and uncertainty in the lending objective. The present dataset cannot prove those properties.
