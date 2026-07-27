from datetime import timedelta

import pytest

from marketpulse.contracts.forecasts import ForecastTarget
from marketpulse.targets.realized_volatility import build_realized_targets
from tests.factories import make_hourly_candles


def test_realized_targets_materialize_two_targets_after_24_hours() -> None:
    candles = make_hourly_candles(30)

    targets = build_realized_targets(candles)

    assert len(targets) == 12
    first_return, first_variance = targets[:2]
    assert first_return.target is ForecastTarget.FORWARD_LOG_RETURN_24H
    assert first_variance.target is ForecastTarget.LOG_REALIZED_VARIANCE_24H
    assert first_return.target_end - first_return.target_start == timedelta(hours=24)
    assert first_return.computed_at >= first_return.target_end


def test_realized_targets_skip_gapped_horizon_and_validate_contract() -> None:
    candles = list(make_hourly_candles(26))
    candles[24] = candles[24].model_copy(
        update={
            "open_time": candles[24].open_time + timedelta(hours=1),
            "close_time": candles[24].close_time + timedelta(hours=1),
            "available_at": candles[24].available_at + timedelta(hours=1),
            "ingested_at": candles[24].ingested_at + timedelta(hours=1),
        }
    )
    assert len(build_realized_targets(candles)) < 4

    with pytest.raises(ValueError, match="only a 24-hour"):
        build_realized_targets(make_hourly_candles(30), horizon_hours=12)
    with pytest.raises(ValueError, match="not enough"):
        build_realized_targets(make_hourly_candles(24))
