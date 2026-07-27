"""Deterministic synthetic market-data factories."""

import math
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from marketpulse.contracts.instruments import INITIAL_UNIVERSE, InstrumentId
from marketpulse.contracts.market import Candle, CandleInterval


def make_hourly_candles(
    count: int,
    *,
    instrument: InstrumentId = INITIAL_UNIVERSE[0],
    start: datetime = datetime(2026, 1, 1, tzinfo=UTC),
    ingestion_lag_seconds: int = 5,
) -> tuple[Candle, ...]:
    """Build a positive, non-constant hourly price path."""
    candles: list[Candle] = []
    previous_close = 100.0
    for index in range(count):
        open_time = start + timedelta(hours=index)
        close = previous_close * math.exp(0.0005 + 0.004 * math.sin(index / 7))
        high = max(previous_close, close) * 1.002
        low = min(previous_close, close) * 0.998
        candles.append(
            Candle(
                instrument=instrument,
                interval=CandleInterval.ONE_HOUR,
                open_time=open_time,
                close_time=open_time + timedelta(hours=1),
                open=Decimal(str(previous_close)),
                high=Decimal(str(high)),
                low=Decimal(str(low)),
                close=Decimal(str(close)),
                volume=Decimal(str(1000 + index % 17)),
                source="binance-usdm",
                available_at=open_time + timedelta(hours=1, seconds=1),
                ingested_at=open_time + timedelta(hours=1, seconds=ingestion_lag_seconds),
            )
        )
        previous_close = close
    return tuple(candles)
