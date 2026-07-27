from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from marketpulse.contracts.instruments import INITIAL_UNIVERSE, InstrumentId
from marketpulse.contracts.market import Candle, CandleInterval


@pytest.fixture
def btc_perpetual() -> InstrumentId:
    return INITIAL_UNIVERSE[0]


@pytest.fixture
def valid_candle(btc_perpetual: InstrumentId) -> Candle:
    open_time = datetime(2026, 1, 1, tzinfo=UTC)
    return Candle(
        instrument=btc_perpetual,
        interval=CandleInterval.ONE_HOUR,
        open_time=open_time,
        close_time=open_time + timedelta(hours=1),
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("98"),
        close=Decimal("103"),
        volume=Decimal("12.5"),
        source="binance-usdm",
        available_at=open_time + timedelta(hours=1, seconds=1),
        ingested_at=open_time + timedelta(hours=1, seconds=3),
    )
