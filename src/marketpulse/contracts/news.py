"""Point-in-time news item contracts."""

from datetime import UTC, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class NewsItem(BaseModel):
    """A deduplicated news record with explicit publication and ingestion time."""

    model_config = ConfigDict(frozen=True)

    source: str = Field(min_length=1, max_length=64)
    external_id: str = Field(min_length=1, max_length=256)
    published_at: datetime
    ingested_at: datetime
    title: str = Field(min_length=1, max_length=1024)
    url: HttpUrl
    language: str = Field(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")

    @field_validator("published_at", "ingested_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        """Reject timestamps that are not explicit UTC values."""
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("timestamps must be timezone-aware UTC values")
        return value

    @model_validator(mode="after")
    def validate_availability(self) -> Self:
        """Ensure ingestion does not precede publication."""
        if self.ingested_at < self.published_at:
            raise ValueError("ingested_at cannot occur before published_at")
        return self
