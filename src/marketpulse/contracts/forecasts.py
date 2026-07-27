"""Forecast and realized-target contracts."""

import math
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from marketpulse.contracts.instruments import InstrumentId

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]


class ForecastTarget(StrEnum):
    """Canonical continuous targets; trading labels are derived policies."""

    LOG_REALIZED_VARIANCE_24H = "log_realized_variance_24h"
    FORWARD_LOG_RETURN_1H = "forward_log_return_1h"
    FORWARD_LOG_RETURN_4H = "forward_log_return_4h"
    FORWARD_LOG_RETURN_24H = "forward_log_return_24h"


class QuantileForecast(BaseModel):
    """An immutable probabilistic forecast with ordered quantiles."""

    model_config = ConfigDict(frozen=True)

    instrument: InstrumentId
    generated_at: datetime
    horizon_hours: int = Field(gt=0, le=168)
    target: ForecastTarget
    model_version: str = Field(min_length=1, max_length=128)
    regime: str = Field(min_length=1, max_length=64)
    p10: FiniteFloat
    p50: FiniteFloat
    p90: FiniteFloat

    @field_validator("generated_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject forecasts without an explicit UTC generation time."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("generated_at must be a timezone-aware UTC value")
        return value

    @model_validator(mode="after")
    def enforce_quantile_order(self) -> Self:
        """Reject crossing probabilistic quantiles."""
        if not self.p10 <= self.p50 <= self.p90:
            raise ValueError("expected p10 <= p50 <= p90")
        return self


class RealizedTarget(BaseModel):
    """A target that becomes available only after its complete horizon."""

    model_config = ConfigDict(frozen=True)

    instrument: InstrumentId
    target: ForecastTarget
    target_start: datetime
    target_end: datetime
    computed_at: datetime
    value: FiniteFloat

    @field_validator("target_start", "target_end", "computed_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject target timestamps that are not explicit UTC values."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("timestamps must be timezone-aware UTC values")
        return value

    @field_validator("value")
    @classmethod
    def require_finite_value(cls, value: float) -> float:
        """Reject non-finite realized values defensively."""
        if not math.isfinite(value):
            raise ValueError("target value must be finite")
        return value

    @model_validator(mode="after")
    def enforce_delayed_materialization(self) -> Self:
        """Prevent target materialization before the horizon closes."""
        if not self.target_start < self.target_end <= self.computed_at:
            raise ValueError("expected target_start < target_end <= computed_at")
        return self
