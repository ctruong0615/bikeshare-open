"""Regression checks for seven-day variability across the mirror's date gap."""
import pandas as pd
import pytest

from src.config import TARGET
from src.features import build_features
from src.ingest import load_raw


@pytest.fixture(scope="module")
def march_raw():
    raw = load_raw()
    return raw.loc[raw.dteday.between("2011-03-01", "2011-03-25")].copy()


def test_gap_and_seven_incomplete_history_days_are_excluded(march_raw):
    missing = pd.Timestamp("2011-03-10")
    assert missing not in set(march_raw.dteday)
    dates = set(build_features(march_raw).dteday)
    assert dates.isdisjoint(pd.date_range("2011-03-10", "2011-03-17"))
    assert pd.Timestamp("2011-03-09") in dates
    assert pd.Timestamp("2011-03-18") in dates


@pytest.mark.parametrize("date", ["2011-03-09", "2011-03-18"])
def test_variability_matches_seven_calendar_days_on_each_side_of_gap(march_raw, date):
    date = pd.Timestamp(date)
    window = pd.date_range(date - pd.Timedelta(days=7), periods=7, freq="D")
    assert (window < date).all()
    counts = march_raw.set_index("dteday").loc[window, TARGET].tolist()
    mean = sum(counts) / 7
    expected = (sum((value - mean) ** 2 for value in counts) / 6) ** 0.5
    actual = build_features(march_raw).set_index("dteday").loc[date, "cnt_roll_std_7"]
    assert actual == pytest.approx(expected)


def test_todays_count_cannot_change_todays_variability(march_raw):
    date = pd.Timestamp("2011-03-18")
    before = build_features(march_raw).set_index("dteday")
    changed = march_raw.copy(deep=True)
    changed.loc[changed.dteday == date, TARGET] += 12345
    after = build_features(changed).set_index("dteday")
    assert after.loc[date, "cnt_roll_std_7"] == pytest.approx(
        before.loc[date, "cnt_roll_std_7"]
    )
    tomorrow = date + pd.Timedelta(days=1)
    assert after.loc[tomorrow, "cnt_roll_std_7"] != pytest.approx(
        before.loc[tomorrow, "cnt_roll_std_7"]
    )
