# A dated extension within the existing credit-risk family

The missing capability is testing whether a model built on earlier observations still works in later periods. More random subdivisions of the same Taiwan or South German cohort cannot establish this. The original loan-level studies remain unchanged.

## Source choice and alternatives

| Candidate | What it can establish | Decision |
|---|---|---|
| Existing South German / Taiwan UCI cohorts | Borrower credit/default labels; no separate calendar outcome cohorts | Preserve the completed studies; cannot solve the dated-evaluation gap |
| Freddie Mac official loan-level history | Mortgage origination and monthly performance dates; closer to borrower credit modelling | Strong future borrower route; official access requires registration and applicable terms. No credentials/terms accepted or mirror substituted in this batch |
| FDIC official financials, institutions and failures | Repeated historical report dates, bank identity, documented failure and inactive dates | Chosen for an independently bounded bank-failure experiment, not as borrower PD evidence |

Sources checked October 10, 2026: [FDIC API documentation](https://api.fdic.gov/banks/docs), [FDIC data-download guide](https://www.fdic.gov/bank-data-guide/data-downloads), [Freddie Mac official dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset).

Official definition files are served at `https://api.fdic.gov/banks/docs/risview_properties.yaml`, `institution_properties.yaml` and `failure_properties.yaml`. The documentation page's slashless relative links resolve incorrectly; acquisition used the actual definitions under `/banks/docs/`. All selected field meanings were checked against those definitions and a small schema probe. Source hashes are retained in the qualification receipt.

## Precisely bounded question

For an FDIC-insured institution with a December 31 financial report, assumed usable on April 1 of the next year, estimate whether its **insurance certificate** has a recorded FDIC failure in the following calendar year. Only institutions still in existence and insured at prediction are eligible. A nonfailure merger/closure or insurance exit during that year is a competing nonfailure outcome. This is the probability of the defined certificate event, not hypothetical failure in a world without mergers, borrower delinquency, bond default, or an IFRS9 provision.

Annual anchors avoid counting the same terminal failure in four overlapping quarterly target windows. They deliberately sacrifice update frequency. Repeated certificates across later annual observations are appropriate for longitudinal monitoring; they are not claimed to be unseen institutions. No bank identifier, current status, closure date, failure date or partition marker is a predictor.

The financial source is a **current historical snapshot**. It can contain corrections and later revisions. A three-month publication delay is conservative as a research convention but is not verified actual per-record availability. Therefore the permitted claim is **retrospective temporal evaluation with a declared availability lag**, not historical point-in-time trading/underwriting performance. The borrower-level out-of-time and original-vintage data gaps remain open.

## Inputs and dates

Nine fixed predictors: equity/assets, net loans/assets, deposits/assets, cash/assets, securities/assets, nonperforming assets/assets, return on assets, net interest margin and nominal log size. `NPERFV`, `ROA` and `NIMY` are already published percentages and are divided by 100. `NIM` is a monetary net-interest-income field and is not substituted for margin. Ratios use compatible monetary units; nominal size is not inflation-adjusted.

All annual reporting dates are genuine source `REPDTE` values. Failure dates come from `FAILDATE` with resolution type **Failure**, excluding **Assistance**. Inactive `ENDEFYMD` and insurance/establishment dates are used only to construct the eligible population and labels. Ambiguous inactive dates, unmatched certificates, invalid assets and contradictory dates are counted and excluded under the registered rules. Ordinary closures remain visible in evaluation, not silently discarded as failures.

The protocol separates development, model selection, calibration, monitoring policy and final later-period evaluation. Entire intervening years are purged so earlier labels are mature before the next stage begins. Imputation/scaling and model fitting see development only. Calibration and policy each use their own later years. The final test is never used to choose features, models, thresholds or a new calibration fit.

## Access, reuse and limits

The official public API explicitly supports building applications from publicly available bank data and presently requires no registration. This batch uses public institutional records, no personal borrower data, credentials or paid service. Attribute FDIC and retain the source disclaimers; no FDIC endorsement or independently audited source correctness is asserted. Repository MIT licensing covers implementation, not an invented licence for third-party source materials. Full API response envelopes and official schemas are not redistributed; compact selected source objects and exact provenance are separate. Replays reconstruct the entire eligible panel, every predictor and every label from those source objects before fitting.

Population coverage, source mismatch exclusions, rare failure counts, regime shift, competing exits, nominal size and current-snapshot revisions must accompany results. Five model stages and a success badge do not prove deployment value. A negative or uncertain later-period comparison remains a valid research finding. The seven flagship identities stay fixed; this is one extension in the credit-risk repository.
