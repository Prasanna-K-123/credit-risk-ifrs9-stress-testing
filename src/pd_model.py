from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import CATEGORICAL_FEATURES, CONTINUOUS_FEATURES, RANDOM_STATE
from src.woe import WOETransformer


@dataclass
class ScorecardModel:
    transformer: WOETransformer
    model: LogisticRegression

    @classmethod
    def fit(cls, X: pd.DataFrame, y: pd.Series) -> "ScorecardModel":
        transformer = WOETransformer(
            continuous_features=CONTINUOUS_FEATURES,
            categorical_features=CATEGORICAL_FEATURES,
            n_bins=5,
        )
        X_woe = transformer.fit_transform(X, y)
        model = LogisticRegression(
            C=1.0,
            solver="lbfgs",
            max_iter=3000,
            random_state=RANDOM_STATE,
        )
        model.fit(X_woe, y)
        return cls(transformer=transformer, model=model)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_woe = self.transformer.transform(X)
        return self.model.predict_proba(X_woe)[:, 1]

    def coefficient_table(self) -> pd.DataFrame:
        coefs = self.model.coef_.ravel()
        return (
            pd.DataFrame(
                {
                    "feature": CONTINUOUS_FEATURES + CATEGORICAL_FEATURES,
                    "coefficient": coefs,
                    "information_value": [
                        self.transformer.iv_[c]
                        for c in CONTINUOUS_FEATURES + CATEGORICAL_FEATURES
                    ],
                }
            )
            .assign(abs_coefficient=lambda d: d["coefficient"].abs())
            .sort_values(["information_value", "abs_coefficient"], ascending=False)
            .drop(columns="abs_coefficient")
        )


def fit_challenger(X: pd.DataFrame, y: pd.Series) -> Pipeline:
    preprocessing = ColumnTransformer(
        transformers=[
            ("continuous", StandardScaler(), CONTINUOUS_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )
    model = RandomForestClassifier(
        n_estimators=600,
        min_samples_leaf=8,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    pipeline = Pipeline([("preprocessing", preprocessing), ("model", model)])
    pipeline.fit(X, y)
    return pipeline
