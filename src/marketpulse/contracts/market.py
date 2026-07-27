"""Point-in-time market data contracts."""

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from marketpulse.contracts.instruments import InstrumentId

PositiveDecimal = Annotated[Decimal, Field(gt=0)]
NonNegativeDecimal = Annotated[Decimal, Field(ge=0)]


class CandleInterval(StrEnum):
    """Supported closed-candle intervals for the MVP."""

    ONE_HOUR = "1h"


class Candle(BaseModel):
    """One immutable, closed OHLCV candle with source and ingestion availability."""

    model_config = ConfigDict(frozen=True)

    instrument: InstrumentId
    interval: CandleInterval
    open_time: datetime
    close_time: datetime
    open: PositiveDecimal
    high: PositiveDecimal
    low: PositiveDecimal
    close: PositiveDecimal
    volume: NonNegativeDecimal
    source: str = Field(min_length=1, max_length=64)
    available_at: datetime
    ingested_at: datetime

    @field_validator("open_time", "close_time", "available_at", "ingested_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject naive or non-UTC timestamps at the contract boundary."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("timestamps must be timezone-aware UTC values")
        return value

    @model_validator(mode="after")
    def validate_temporal_and_price_integrity(self) -> Self:
        """Validate closed-candle timing and OHLC coherence."""
        if not self.open_time < self.close_time <= self.available_at <= self.ingested_at:
            raise ValueError("expected open_time < close_time <= available_at <= ingested_at")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be greater than or equal to all OHLC prices")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be less than or equal to all OHLC prices")
        return self
