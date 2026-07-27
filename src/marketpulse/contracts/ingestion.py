"""Contracts for immutable market-data ingestion and quality evidence."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from marketpulse.contracts.instruments import InstrumentId
from marketpulse.contracts.market import CandleInterval


class QualitySeverity(StrEnum):
    """Severity levels emitted by deterministic data-quality checks."""

    ERROR = "error"
    WARNING = "warning"


class QualityIssue(BaseModel):
    """One machine-readable quality finding."""

    model_config = ConfigDict(frozen=True)

    code: str = Field(pattern=r"^[A-Z][A-Z0-9_]{2,63}$")
    severity: QualitySeverity
    message: str = Field(min_length=1, max_length=512)
    event_time: datetime | None = None

    @field_validator("event_time")
    @classmethod
    def require_utc(cls, value: datetime | None) -> datetime | None:
        """Reject non-UTC issue timestamps."""
        if value is not None and (
            value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value)
        ):
            raise ValueError("event_time must be timezone-aware UTC")
        return value


class CandleQualityReport(BaseModel):
    """Deterministic validation report for a homogeneous candle batch."""

    model_config = ConfigDict(frozen=True)

    instrument: InstrumentId
    interval: CandleInterval
    checked_at: datetime
    record_count: int = Field(ge=0)
    expected_count: int = Field(ge=0)
    freshness_seconds: float = Field(ge=0, allow_inf_nan=False)
    issues: tuple[QualityIssue, ...] = ()

    @field_validator("checked_at")
    @classmethod
    def require_checked_at_utc(cls, value: datetime) -> datetime:
        """Reject validation timestamps without explicit UTC."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("checked_at must be timezone-aware UTC")
        return value

    @property
    def error_count(self) -> int:
        """Return the number of blocking findings."""
        return sum(issue.severity is QualitySeverity.ERROR for issue in self.issues)

    @property
    def warning_count(self) -> int:
        """Return the number of non-blocking findings."""
        return sum(issue.severity is QualitySeverity.WARNING for issue in self.issues)


class IngestionManifest(BaseModel):
    """Lineage manifest for one immutable Parquet partition object."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "market-candles-v1"
    source: str = Field(min_length=1, max_length=64)
    instrument: InstrumentId
    exchange_contract_type: str = Field(min_length=1, max_length=64)
    interval: CandleInterval
    partition_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    object_path: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    record_count: int = Field(gt=0)
    first_open_time: datetime
    last_close_time: datetime
    created_at: datetime

    @field_validator("first_open_time", "last_close_time", "created_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject lineage timestamps without explicit UTC."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("manifest timestamps must be timezone-aware UTC")
        return value
