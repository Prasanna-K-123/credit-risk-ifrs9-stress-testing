from __future__ import annotations

from io import BytesIO
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import RANDOM_STATE


UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/522/south+german+credit.zip"
UCI_DATA_FILE = "SouthGermanCredit.asc"

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
    lowered = s.astype(str).str.strip().str.lower()
    if set(lowered.unique()).issubset({"good", "bad"}):
        return lowered.map({"good": 0, "bad": 1}).astype(int).rename("default")

    numeric = pd.to_numeric(s, errors="raise").astype(int)
    unique = set(numeric.unique())
    if unique != {0, 1}:
        raise ValueError(f"Unexpected target encoding: {sorted(unique)}")

    # Corrected South German Credit coding: 0=bad, 1=good.
    return (1 - numeric).astype(int).rename("default")


def load_south_german_credit() -> tuple[pd.DataFrame, pd.Series]:
    """Download the corrected South German Credit source from UCI.

    The official archive contains 1,000 observations and 20 predictors. Raw
    target coding is 0=bad and 1=good; the modelling convention used here is
    ``default=1`` for a bad/default outcome.
    """
    request = Request(UCI_ZIP_URL, headers={"User-Agent": "credit-risk-research/1.0"})
    with urlopen(request, timeout=30) as response:  # nosec B310 - fixed HTTPS UCI URL
        archive_bytes = response.read()

    with ZipFile(BytesIO(archive_bytes)) as archive:
        with archive.open(UCI_DATA_FILE) as handle:
            raw = pd.read_csv(handle, sep=r"\s+")

    raw = _standardize_columns(raw)
    if "credit_risk" not in raw.columns:
        raise RuntimeError("UCI source schema changed: credit_risk target not found.")

    y = _to_default_target(raw.pop("credit_risk"))
    X = raw
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
