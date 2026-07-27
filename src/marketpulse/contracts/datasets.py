"""Point-in-time training and evaluation dataset contracts."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from marketpulse.contracts.forecasts import ForecastTarget, QuantileForecast
from marketpulse.contracts.instruments import InstrumentId


class TrainingRow(BaseModel):
    """One leakage-safe feature/target observation available by a cutoff."""

    model_config = ConfigDict(frozen=True)

    instrument: InstrumentId
    prediction_time: datetime
    feature_time: datetime
    feature_availability_time: datetime
    target_computed_at: datetime
    target: ForecastTarget
    features: dict[str, float] = Field(min_length=1)
    value: float = Field(allow_inf_nan=False)

    @field_validator(
        "prediction_time", "feature_time", "feature_availability_time", "target_computed_at"
    )
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject dataset timestamps without explicit UTC."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("dataset timestamps must be timezone-aware UTC")
        return value

    @model_validator(mode="after")
    def validate_point_in_time_order(self) -> "TrainingRow":
        """Ensure features precede prediction and target availability follows it."""
        if self.feature_time > self.feature_availability_time:
            raise ValueError("feature_time cannot follow feature availability")
        if self.feature_availability_time > self.prediction_time:
            raise ValueError("feature availability cannot occur after prediction")
        if self.target_computed_at <= self.prediction_time:
            raise ValueError("target must materialize after prediction")
        return self


class DatasetManifest(BaseModel):
    """Reproducible identity and coverage of a training dataset."""

    model_config = ConfigDict(frozen=True)

    dataset_version: str = Field(min_length=1, max_length=64)
    dataset_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    cutoff: datetime
    target: ForecastTarget
    row_count: int = Field(ge=0)
    first_prediction_time: datetime | None
    last_prediction_time: datetime | None

    @field_validator("cutoff", "first_prediction_time", "last_prediction_time")
    @classmethod
    def require_utc(cls, value: datetime | None) -> datetime | None:
        """Reject manifest timestamps without explicit UTC."""
        if value is not None and (
            value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value)
        ):
            raise ValueError("dataset manifest timestamps must be timezone-aware UTC")
        return value


class ForecastEvaluationRow(BaseModel):
    """Out-of-sample forecast paired with its realized value and fold."""

    model_config = ConfigDict(frozen=True)

    fold: int = Field(ge=0)
    forecast: QuantileForecast
    actual: float = Field(allow_inf_nan=False)
    target_computed_at: datetime

    @field_validator("target_computed_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject non-UTC target materialization timestamps."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("target_computed_at must be timezone-aware UTC")
        return value
