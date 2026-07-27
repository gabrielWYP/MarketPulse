import math

import pytest

from marketpulse.features.market_v1 import build_market_v1_features
from tests.factories import make_hourly_candles


def test_market_v1_uses_only_closed_trailing_window() -> None:
    candles = make_hourly_candles(30)

    snapshots = build_market_v1_features(candles)

    assert len(snapshots) == 6
    first = snapshots[0]
    assert first.feature_time == candles[24].close_time
    assert first.availability_time == candles[24].available_at
    assert first.prediction_time == first.availability_time
    assert set(first.features) == {
        "log_return_1h",
        "log_return_6h",
        "log_return_24h",
        "log_realized_variance_24h",
        "parkinson_variance_24h",
        "volume_zscore_24h",
        "range_fraction_1h",
    }
    assert all(math.isfinite(value) for value in first.features.values())


def test_market_v1_rejects_short_or_duplicate_series() -> None:
    with pytest.raises(ValueError, match="25"):
        build_market_v1_features(make_hourly_candles(24))

    candles = make_hourly_candles(25)
    with pytest.raises(ValueError, match="duplicate"):
        build_market_v1_features((*candles[:-1], candles[-2]))
