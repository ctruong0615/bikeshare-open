"""The tests that make the agent honest.

test_no_forbidden_features is the single most valuable test in this repo:
casual + registered == cnt exactly, so any model handed those columns
scores R^2 = 1.0 and looks brilliant while having learned nothing.
"""
from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from src.config import FORBIDDEN, TARGET
from src.features import build_features, encode_weather, feature_columns
from src.ingest import load_raw


@pytest.fixture(scope="module")
def feats():
    return build_features(load_raw())


def test_leakage_identity_holds(feats):
    """Documents *why* casual and registered are forbidden."""
    assert (feats.casual + feats.registered == feats[TARGET]).all()


def test_no_forbidden_features(feats):
    """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
    construction, so this cannot discover a *new* leaky column. What it
    catches is someone editing feature_columns() or FORBIDDEN -- which is
    exactly the fault the Step 7 hook demonstrates."""
    cols = set(feature_columns(feats))
    assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"


def test_lags_are_true_calendar_lags(feats):
    """cnt_lag_1 for date d must equal cnt on d-1, in calendar days."""
    by_date = feats.set_index("dteday")[TARGET]
    checked = 0
    for date, lag in feats.set_index("dteday").cnt_lag_1.items():
        prev = date - pd.Timedelta(days=1)
        if prev in by_date.index:
            assert lag == pytest.approx(by_date[prev]), f"bad lag at {date.date()}"
            checked += 1
    assert checked > 600, "too few rows actually verified"


def test_lag_is_not_the_target(feats):
    assert not (feats.cnt_lag_1 == feats[TARGET]).all()


def test_rolling_mean_excludes_today(feats):
    """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
    by_date = feats.set_index("dteday")[TARGET]
    date = feats.dteday.iloc[200]
    window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
    if all(d in by_date.index for d in window):
        expected = sum(by_date[d] for d in window) / 7
        assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)


def test_no_missing_values(feats):
    assert feats[feature_columns(feats)].isna().sum().sum() == 0


def test_dates_are_sorted_and_unique(feats):
    assert feats.dteday.is_monotonic_increasing
    assert feats.dteday.is_unique


def test_unknown_weather_fails_loudly():
    with pytest.raises(ValueError, match="unmapped weather labels"):
        encode_weather(pd.Series(["GOOD", "UNEXPECTED_WEATHER"]))


def test_cnt_roll_std_7_on_2011_01_10(feats):
    """Sample std from Jan 3--9; Jan 10's count must not enter the window."""
    counts = [1349, 1562, 1600, 1606, 1510, 959, 822]
    raw = load_raw().set_index("dteday")
    dates = pd.date_range("2011-01-03", "2011-01-09", freq="D")
    assert raw.loc[dates, TARGET].tolist() == counts
    mean = sum(counts) / 7
    expected = (sum((value - mean) ** 2 for value in counts) / 6) ** 0.5
    assert feats.set_index("dteday").loc[
        pd.Timestamp("2011-01-10"), "cnt_roll_std_7"
    ] == pytest.approx(expected)


def test_no_exact_target_identity_in_model_inputs(feats):
    """Inspect values so an innocently renamed target cannot hide in inputs."""
    cols = feature_columns(feats)
    y = feats[TARGET].to_numpy(dtype=float)
    for size in (1, 2, 3):
        for subset in combinations(cols, size):
            X = np.column_stack([feats[list(subset)].to_numpy(dtype=float),
                                 np.ones(len(feats))])
            coef, *_ = np.linalg.lstsq(X, y, rcond=None)
            residual = np.abs(X @ coef - y).max()
            assert residual > 1e-6, f"exact target identity in features: {subset}"
