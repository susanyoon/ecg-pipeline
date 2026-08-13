import numpy as np
import pandas as pd

from ecg.model import prepare_xy, split_by_fold, train_model


def make_frame():
    return pd.DataFrame(
        {
            "ecg_id": range(100),
            "heart_rate": np.random.uniform(50, 100, 100),
            "mean_rr": np.random.uniform(0.6, 1.2, 100),
            "rr_std": np.random.uniform(0.01, 0.3, 100),
            "age": np.random.randint(20, 90, 100),
            "sex": np.random.randint(0, 2, 100),
            "strat_fold": [10 if i < 20 else 1 for i in range(100)],
            "is_normal": np.random.randint(0, 2, 100),
        }
    )


def test_split_uses_fold_ten_as_test():
    df = make_frame()
    train, test = split_by_fold(df)
    assert len(test) == 20
    assert len(train) == 80
    assert (test["strat_fold"] == 10).all()
    assert (train["strat_fold"] != 10).all()


def test_prepare_xy_shapes():
    df = make_frame()
    X, y = prepare_xy(df)
    assert X.shape[0] == len(y)
    assert X.shape[1] == 5  # five feature columns


def test_prepare_xy_drops_missing():
    df = make_frame()
    df.loc[0, "heart_rate"] = np.nan
    X, y = prepare_xy(df)
    assert len(X) == 99


def test_model_trains_and_predicts():
    df = make_frame()
    X, y = prepare_xy(df)
    model = train_model(X, y)
    preds = model.predict(X)
    assert len(preds) == len(y)
    assert set(preds).issubset({0, 1})
