from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

FEATURE_COLUMNS = ["heart_rate", "mean_rr", "rr_std", "age", "sex"]
TEST_FOLD = 10  # PTB-XL's recommended held-out test fold


def split_by_fold(df: pd.DataFrame, test_fold: int = TEST_FOLD):
    """
    Split using PTB-XL's official stratified folds.

    Fold 10 is the dataset's recommended test set. Using it (rather than a random split)
    keeps results comparable to published work and avoids patient leakage
    across the split.
    """
    train = df[df["strat_fold"] != test_fold]
    test = df[df["strat_fold"] == test_fold]
    return train, test


def prepare_xy(df: pd.DataFrame):
    """
    Extract feature matrix & labels, dropping rows w/ missing values.
    """
    subset = df.dropna(subset=FEATURE_COLUMNS + ["is_normal"])
    X = subset[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = subset["is_normal"].to_numpy(dtype=int)
    return X, y


def train_model(X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
    """
    Fit a random forest baseline.

    `class_weight="balanced"` counteracts class imbalance so the model
    isn't rewarded for simply predicting the majority class.
    """
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    """
    Evaluate honestly: per-class precision/recall, confusion matrix, AUC.

    Accuracy is deliberately not the headline metric
    (on imbalanced clinical data it can look high while
    the model misses the minority class).
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    return {
        "report": classification_report(
            y_test, y_pred, target_names=["Abnormal", "Normal"], output_dict=True
        ),
        "report_text": classification_report(
            y_test, y_pred, target_names=["Abnormal", "Normal"]
        ),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "n_train_positive_rate": None,  # filled by the caller if desired
    }
