# Data provenance

## Separate dated institutional-risk extension

The [FDIC retrospective temporal study](../docs/FDIC_TEMPORAL_REVIEW.md) uses official institutional financial, insurance/closure and failure records. Its 31 compact original-source extracts are pinned under `reference/fdic_temporal/` so every eligible row, predictor and label can be reconstructed without mutable live API calls. [The source receipt](../reference/fdic_temporal/source_snapshot.json) records full queries, indices, counts and hashes. These are current historical values, with an assumed April 1 availability lag; original-release vintages are not available. The target is bank-certificate failure with competing nonfailure exits, not borrower PD. FDIC source attribution and disclaimers remain separate from the implementation's MIT licence.

## Original South German borrower study

The modelling pipeline downloads **South German Credit** directly from the official UCI Machine Learning Repository archive for dataset id **522** and reads `SouthGermanCredit.asc` from the published ZIP.

Official UCI DOI: `10.24432/C5X89F`.

The dataset contains 1,000 historical credit observations, 20 predictors and a binary credit-risk outcome. UCI documents 700 good and 300 bad credits, no missing values, and notes that bad credits were deliberately oversampled.

The original South German raw data are intentionally **not copied into this repository**. Run `python run_pipeline.py` to fetch that UCI source and regenerate its evidence.

## Critical suitability limits

This dataset does **not** contain:

- observation/performance dates required for genuine out-of-time validation;
- recovery cash flows required for empirical LGD estimation;
- undrawn commitments/utilisation paths required for empirical EAD/CCF estimation;
- institution-specific default/cure definitions;
- macroeconomic histories for IFRS 9 scenario calibration;
- contractual effective interest rates.

Accordingly, this project treats PD modelling as empirical and uses clearly labelled **illustrative** assumptions for LGD, scenario severity and ECL demonstration mechanics. The observed credit amount is used only as a drawn-EAD proxy in the demo.

This separation is intentional: the repository does not manufacture empirical LGD/EAD claims that the source data cannot support.
