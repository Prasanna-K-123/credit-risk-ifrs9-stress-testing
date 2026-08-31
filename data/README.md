# Data provenance

The modelling pipeline downloads **South German Credit** directly from the UCI Machine Learning Repository using `ucimlrepo` dataset id **522**.

Official UCI DOI: `10.24432/C5X89F`.

The dataset contains 1,000 historical credit observations, 20 predictors and a binary credit-risk outcome. UCI documents 700 good and 300 bad credits, no missing values, and notes that bad credits were deliberately oversampled.

Raw data are intentionally **not copied into this repository**. Run `python run_pipeline.py` to fetch the UCI source and regenerate all evidence.

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
