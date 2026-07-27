from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from marketpulse.contracts.market import Candle


def test_valid_candle_is_closed_before_ingestion(valid_candle: Candle) -> None:
    assert valid_candle.close_time <= valid_candle.ingested_at


def test_candle_rejects_incoherent_high(valid_candle: Candle) -> None:
    payload = valid_candle.model_dump()
    payload["high"] = Decimal("99")

    with pytest.raises(ValidationError, match="high"):
        Candle.model_validate(payload)


def test_candle_rejects_future_close(valid_candle: Candle) -> None:
    payload = valid_candle.model_dump()
    payload["ingested_at"] = valid_candle.close_time - timedelta(seconds=1)

    with pytest.raises(ValidationError, match="close_time"):
        Candle.model_validate(payload)


def test_candle_rejects_incoherent_low(valid_candle: Candle) -> None:
    payload = valid_candle.model_dump()
    payload["low"] = Decimal("104")

    with pytest.raises(ValidationError, match="low"):
        Candle.model_validate(payload)


def test_candle_rejects_naive_timestamp(valid_candle: Candle) -> None:
    payload = valid_candle.model_dump()
    payload["open_time"] = datetime(2026, 1, 1)

    with pytest.raises(ValidationError, match="UTC"):
        Candle.model_validate(payload)
