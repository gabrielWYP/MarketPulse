"""Quality validation for homogeneous hourly candle ranges."""

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from marketpulse.contracts.ingestion import (
    CandleQualityReport,
    QualityIssue,
    QualitySeverity,
)
from marketpulse.contracts.market import Candle, CandleInterval

_HOUR = timedelta(hours=1)


class CandleQualityError(ValueError):
    """Raised when a candle batch contains blocking quality findings."""

    def __init__(self, report: CandleQualityReport) -> None:
        """Retain the full report for structured pipeline diagnostics."""
        self.report = report
        super().__init__(f"candle quality failed with {report.error_count} blocking issue(s)")


def validate_candles(
    candles: Sequence[Candle],
    *,
    expected_start: datetime,
    expected_end: datetime,
    checked_at: datetime | None = None,
    missing_is_error: bool = True,
) -> CandleQualityReport:
    """Validate range coverage, duplicates, cadence, and freshness."""
    _validate_range(expected_start, expected_end)
    if not candles:
        raise ValueError("cannot validate an empty candle batch")
    timestamp = checked_at or datetime.now(UTC)
    _require_utc(timestamp, "checked_at")
    first = candles[0]
    issues: list[QualityIssue] = []
    if any(
        candle.instrument != first.instrument or candle.interval is not first.interval
        for candle in candles
    ):
        issues.append(
            QualityIssue(
                code="MIXED_BATCH",
                severity=QualitySeverity.ERROR,
                message="batch contains multiple instruments or intervals",
            )
        )
    counts = Counter(candle.open_time for candle in candles)
    for event_time, count in sorted(counts.items()):
        if count > 1:
            issues.append(
                QualityIssue(
                    code="DUPLICATE_CANDLE",
                    severity=QualitySeverity.ERROR,
                    message=f"found {count} rows for one open_time",
                    event_time=event_time,
                )
            )
    actual_times = set(counts)
    expected_times = _hourly_range(expected_start, expected_end)
    missing_severity = QualitySeverity.ERROR if missing_is_error else QualitySeverity.WARNING
    for event_time in sorted(expected_times - actual_times):
        issues.append(
            QualityIssue(
                code="MISSING_CANDLE",
                severity=missing_severity,
                message="expected hourly candle is absent",
                event_time=event_time,
            )
        )
    for event_time in sorted(actual_times - expected_times):
        issues.append(
            QualityIssue(
                code="OUT_OF_RANGE_CANDLE",
                severity=QualitySeverity.ERROR,
                message="candle falls outside requested range",
                event_time=event_time,
            )
        )
    for candle in candles:
        if candle.close_time - candle.open_time != _HOUR:
            issues.append(
                QualityIssue(
                    code="INVALID_CADENCE",
                    severity=QualitySeverity.ERROR,
                    message="hourly candle duration is not exactly one hour",
                    event_time=candle.open_time,
                )
            )
    latest_close = max(candle.close_time for candle in candles)
    freshness = max((timestamp - latest_close).total_seconds(), 0.0)
    report = CandleQualityReport(
        instrument=first.instrument,
        interval=CandleInterval.ONE_HOUR,
        checked_at=timestamp,
        record_count=len(candles),
        expected_count=len(expected_times),
        freshness_seconds=freshness,
        issues=tuple(issues),
    )
    if report.error_count:
        raise CandleQualityError(report)
    return report


def _hourly_range(start: datetime, end: datetime) -> set[datetime]:
    return {start + index * _HOUR for index in range(int((end - start) / _HOUR))}


def _validate_range(start: datetime, end: datetime) -> None:
    _require_utc(start, "expected_start")
    _require_utc(end, "expected_end")
    if start >= end:
        raise ValueError("expected_start must be earlier than expected_end")
    if any((value.minute, value.second, value.microsecond) != (0, 0, 0) for value in (start, end)):
        raise ValueError("expected range must align to UTC hours")


def _require_utc(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")
