from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from marketpulse.contracts.features import FeatureSnapshot
from marketpulse.contracts.instruments import InstrumentId


def test_feature_snapshot_rejects_future_availability(
    btc_perpetual: InstrumentId,
) -> None:
    prediction_time = datetime(2026, 1, 1, 12, tzinfo=UTC)

    with pytest.raises(ValidationError, match="availability_time"):
        FeatureSnapshot(
            instrument=btc_perpetual,
            feature_time=prediction_time - timedelta(hours=1),
            availability_time=prediction_time + timedelta(seconds=1),
            prediction_time=prediction_time,
            feature_set_version="market_v1",
            features={"return_1h": 0.01},
        )


def test_feature_snapshot_rejects_non_finite_values(
    btc_perpetual: InstrumentId,
) -> None:
    prediction_time = datetime(2026, 1, 1, 12, tzinfo=UTC)

    with pytest.raises(ValidationError, match="finite"):
        FeatureSnapshot(
            instrument=btc_perpetual,
            feature_time=prediction_time,
            availability_time=prediction_time,
            prediction_time=prediction_time,
            feature_set_version="market_v1",
            features={"broken": float("nan")},
        )


def test_feature_snapshot_rejects_feature_time_after_availability(
    btc_perpetual: InstrumentId,
) -> None:
    prediction_time = datetime(2026, 1, 1, 12, tzinfo=UTC)

    with pytest.raises(ValidationError, match="feature_time"):
        FeatureSnapshot(
            instrument=btc_perpetual,
            feature_time=prediction_time,
            availability_time=prediction_time - timedelta(seconds=1),
            prediction_time=prediction_time,
            feature_set_version="market_v1",
            features={"return_1h": 0.01},
        )


def test_feature_snapshot_rejects_naive_timestamp(
    btc_perpetual: InstrumentId,
) -> None:
    naive_time = datetime(2026, 1, 1, 12)

    with pytest.raises(ValidationError, match="UTC"):
        FeatureSnapshot(
            instrument=btc_perpetual,
            feature_time=naive_time,
            availability_time=naive_time,
            prediction_time=naive_time,
            feature_set_version="market_v1",
            features={"return_1h": 0.01},
        )
