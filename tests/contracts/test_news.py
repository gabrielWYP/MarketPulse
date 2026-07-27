from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from marketpulse.contracts.news import NewsItem


def valid_news_payload() -> dict[str, object]:
    published_at = datetime(2026, 1, 1, tzinfo=UTC)
    return {
        "source": "example-wire",
        "external_id": "article-1",
        "published_at": published_at,
        "ingested_at": published_at + timedelta(seconds=5),
        "title": "A point-in-time market event",
        "url": "https://example.com/article-1",
        "language": "en",
        "content_hash": "a" * 64,
    }


def test_news_item_accepts_delayed_ingestion() -> None:
    item = NewsItem.model_validate(valid_news_payload())

    assert item.ingested_at > item.published_at


def test_news_item_rejects_ingestion_before_publication() -> None:
    payload = valid_news_payload()
    payload["ingested_at"] = datetime(2025, 12, 31, 23, 59, tzinfo=UTC)

    with pytest.raises(ValidationError, match="ingested_at"):
        NewsItem.model_validate(payload)


def test_news_item_rejects_naive_timestamp() -> None:
    payload = valid_news_payload()
    payload["published_at"] = datetime(2026, 1, 1)

    with pytest.raises(ValidationError, match="UTC"):
        NewsItem.model_validate(payload)
