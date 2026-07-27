"""Point-in-time feature snapshot contracts."""

import math
from datetime import UTC, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from marketpulse.contracts.instruments import InstrumentId


class FeatureSnapshot(BaseModel):
    """Versioned features whose availability is bounded by prediction time."""

    model_config = ConfigDict(frozen=True)

    instrument: InstrumentId
    feature_time: datetime
    availability_time: datetime
    prediction_time: datetime
    feature_set_version: str = Field(min_length=1, max_length=64)
    features: dict[str, float] = Field(min_length=1)

    @field_validator("feature_time", "availability_time", "prediction_time")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject timestamps that are not explicit UTC values."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("timestamps must be timezone-aware UTC values")
        return value

    @field_validator("features")
    @classmethod
    def require_finite_features(cls, value: dict[str, float]) -> dict[str, float]:
        """Reject NaN and infinite feature values at the contract boundary."""
        if any(not math.isfinite(feature_value) for feature_value in value.values()):
            raise ValueError("features must contain only finite values")
        return value

    @model_validator(mode="after")
    def prevent_temporal_leakage(self) -> Self:
        """Enforce point-in-time availability before prediction."""
        if self.feature_time > self.availability_time:
            raise ValueError("feature_time cannot occur after availability_time")
        if self.availability_time > self.prediction_time:
            raise ValueError("availability_time cannot occur after prediction_time")
        return self
