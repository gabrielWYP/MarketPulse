from datetime import UTC, datetime, timedelta

import pytest

from marketpulse.quality.candles import CandleQualityError, validate_candles
from tests.factories import make_hourly_candles


def test_valid_candle_range_has_no_findings() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    candles = make_hourly_candles(3, start=start)

    report = validate_candles(
        candles,
        expected_start=start,
        expected_end=start + timedelta(hours=3),
        checked_at=start + timedelta(hours=4),
    )

    assert report.error_count == 0
    assert report.warning_count == 0
    assert report.freshness_seconds == 3600


def test_missing_candle_can_warn_or_block() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    candles = make_hourly_candles(3, start=start)
    missing_middle = (candles[0], candles[2])

    warning = validate_candles(
        missing_middle,
        expected_start=start,
        expected_end=start + timedelta(hours=3),
        checked_at=start + timedelta(hours=3),
        missing_is_error=False,
    )
    assert warning.warning_count == 1
    assert warning.issues[0].code == "MISSING_CANDLE"

    with pytest.raises(CandleQualityError) as captured:
        validate_candles(
            missing_middle,
            expected_start=start,
            expected_end=start + timedelta(hours=3),
            checked_at=start + timedelta(hours=3),
        )
    assert captured.value.report.error_count == 1


def test_duplicate_candle_is_blocking() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    candles = make_hourly_candles(2, start=start)

    with pytest.raises(CandleQualityError, match="blocking") as captured:
        validate_candles(
            (candles[0], candles[0], candles[1]),
            expected_start=start,
            expected_end=start + timedelta(hours=2),
            checked_at=start + timedelta(hours=2),
        )
    assert any(issue.code == "DUPLICATE_CANDLE" for issue in captured.value.report.issues)


def test_quality_rejects_empty_or_invalid_range() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    with pytest.raises(ValueError, match="empty"):
        validate_candles([], expected_start=start, expected_end=start + timedelta(hours=1))
    with pytest.raises(ValueError, match="earlier"):
        validate_candles(
            make_hourly_candles(1),
            expected_start=start,
            expected_end=start,
        )
