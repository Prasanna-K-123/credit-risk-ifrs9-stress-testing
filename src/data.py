from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo

from src.config import RANDOM_STATE


GERMAN_TO_ENGLISH = {
    "laufkont": "status",
    "laufzeit": "duration",
    "moral": "credit_history",
    "verw": "purpose",
    "hoehe": "amount",
    "sparkont": "savings",
    "beszeit": "employment_duration",
    "rate": "installment_rate",
    "famges": "personal_status_sex",
    "buerge": "other_debtors",
    "wohnzeit": "present_residence",
    "verm": "property",
    "alter": "age",
    "weitkred": "other_installment_plans",
    "wohn": "housing",
    "bishkred": "number_credits",
    "beruf": "job",
    "pers": "people_liable",
    "telef": "telephone",
    "gastarb": "foreign_worker",
    "kredit": "credit_risk",
}


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [GERMAN_TO_ENGLISH.get(str(c), str(c)) for c in out.columns]
    return out


def _to_default_target(raw_y: pd.Series) -> pd.Series:
    """Return target as 1=bad/default and 0=good/non-default."""
    s = pd.Series(raw_y).copy()

    # String/factor labels if a client version exposes semantic levels.
    lowered = s.astype(str).str.strip().str.lower()
    if set(lowered.unique()).issubset({"good", "bad"}):
        return lowered.map({"good": 0, "bad": 1}).astype(int).rename("default")

    numeric = pd.to_numeric(s, errors="raise").astype(int)
    unique = set(numeric.unique())
    if unique != {0, 1}:
        raise ValueError(f"Unexpected target encoding: {sorted(unique)}")

    # Grömping's corrected South German Credit coding: 0=bad, 1=good.
    return (1 - numeric).astype(int).rename("default")


def load_south_german_credit() -> tuple[pd.DataFrame, pd.Series]:
    """Fetch the corrected South German Credit dataset from UCI.

    UCI dataset id 573 has 1,000 observations, 20 predictors and no missing
    values. The corrected source coding is 0=bad and 1=good; this function
    standardizes the modelling target to ``default=1`` for bad/default.
    """
    dataset = fetch_ucirepo(id=573)
    X = _standardize_columns(dataset.data.features.copy())
    raw_y = dataset.data.targets.copy()

    if isinstance(raw_y, pd.DataFrame):
        raw_y = _standardize_columns(raw_y)
        if "credit_risk" in raw_y.columns:
            raw_y = raw_y["credit_risk"]
        else:
            raw_y = raw_y.iloc[:, 0]

    y = _to_default_target(raw_y)
    return X, y


def development_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.20,
    validation_size: float = 0.20,
):
    """Create stratified train/validation/test samples.

    The source data have no observation dates, so this is deliberately NOT
    described as an out-of-time split.
    """
    X_dev, X_test, y_dev, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    val_fraction_of_dev = validation_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_dev,
        y_dev,
        test_size=val_fraction_of_dev,
        stratify=y_dev,
        random_state=RANDOM_STATE,
    )
    return X_train, X_val, X_test, y_train, y_val, y_test
