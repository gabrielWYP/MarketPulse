from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from marketpulse.contracts.forecasts import ForecastTarget, QuantileForecast, RealizedTarget
from marketpulse.contracts.instruments import InstrumentId


def test_quantile_forecast_requires_ordered_quantiles(
    btc_perpetual: InstrumentId,
) -> None:
    with pytest.raises(ValidationError, match="p10 <= p50 <= p90"):
        QuantileForecast(
            instrument=btc_perpetual,
            generated_at=datetime(2026, 1, 1, tzinfo=UTC),
            horizon_hours=24,
            target=ForecastTarget.LOG_REALIZED_VARIANCE_24H,
            model_version="baseline-v1",
            regime="normal",
            p10=-2.0,
            p50=-3.0,
            p90=-1.0,
        )


def test_realized_target_is_materialized_after_horizon(
    btc_perpetual: InstrumentId,
) -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    target = RealizedTarget(
        instrument=btc_perpetual,
        target=ForecastTarget.FORWARD_LOG_RETURN_24H,
        target_start=start,
        target_end=start + timedelta(hours=24),
        computed_at=start + timedelta(hours=24, seconds=1),
        value=0.05,
    )

    assert target.computed_at > target.target_end


def test_forecast_rejects_naive_generation_time(
    btc_perpetual: InstrumentId,
) -> None:
    with pytest.raises(ValidationError, match="UTC"):
        QuantileForecast(
            instrument=btc_perpetual,
            generated_at=datetime(2026, 1, 1),
            horizon_hours=24,
            target=ForecastTarget.LOG_REALIZED_VARIANCE_24H,
            model_version="baseline-v1",
            regime="normal",
            p10=-3.0,
            p50=-2.0,
            p90=-1.0,
        )


def test_realized_target_rejects_early_materialization(
    btc_perpetual: InstrumentId,
) -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    with pytest.raises(ValidationError, match="target_start"):
        RealizedTarget(
            instrument=btc_perpetual,
            target=ForecastTarget.FORWARD_LOG_RETURN_24H,
            target_start=start,
            target_end=start + timedelta(hours=24),
            computed_at=start + timedelta(hours=23),
            value=0.05,
        )


def test_realized_target_rejects_naive_timestamp(
    btc_perpetual: InstrumentId,
) -> None:
    naive_time = datetime(2026, 1, 1)

    with pytest.raises(ValidationError, match="UTC"):
        RealizedTarget(
            instrument=btc_perpetual,
            target=ForecastTarget.FORWARD_LOG_RETURN_1H,
            target_start=naive_time,
            target_end=naive_time + timedelta(hours=1),
            computed_at=naive_time + timedelta(hours=1),
            value=0.01,
        )
