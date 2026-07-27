from datetime import UTC, datetime

import pytest

from marketpulse.contracts.forecasts import ForecastTarget
from marketpulse.datasets.builder import build_training_dataset
from marketpulse.features.market_v1 import build_market_v1_features
from marketpulse.targets.realized_volatility import build_realized_targets
from tests.factories import make_hourly_candles


def test_dataset_builder_respects_cutoff_and_is_reproducible() -> None:
    candles = make_hourly_candles(80)
    features = build_market_v1_features(candles)
    targets = build_realized_targets(candles)
    cutoff = candles[-1].ingested_at

    first = build_training_dataset(
        features,
        targets,
        target=ForecastTarget.FORWARD_LOG_RETURN_24H,
        cutoff=cutoff,
    )
    second = build_training_dataset(
        features,
        targets,
        target=ForecastTarget.FORWARD_LOG_RETURN_24H,
        cutoff=cutoff,
    )

    assert first == second
    assert first.manifest.row_count == len(first.rows)
    assert first.rows
    assert all(row.target_computed_at <= cutoff for row in first.rows)
    assert all(row.feature_availability_time <= row.prediction_time for row in first.rows)


def test_dataset_builder_rejects_naive_cutoff() -> None:
    with pytest.raises(ValueError, match="UTC"):
        build_training_dataset(
            [],
            [],
            target=ForecastTarget.LOG_REALIZED_VARIANCE_24H,
            cutoff=datetime(2026, 1, 1),
        )


def test_earlier_cutoff_excludes_unavailable_targets() -> None:
    candles = make_hourly_candles(80)
    cutoff = datetime(2026, 1, 3, tzinfo=UTC)
    dataset = build_training_dataset(
        build_market_v1_features(candles),
        build_realized_targets(candles),
        target=ForecastTarget.LOG_REALIZED_VARIANCE_24H,
        cutoff=cutoff,
    )
    assert all(row.target_computed_at <= cutoff for row in dataset.rows)
