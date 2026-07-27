from datetime import UTC, datetime

from marketpulse.contracts.ingestion import CandleQualityReport, QualityIssue, QualitySeverity
from marketpulse.contracts.instruments import INITIAL_UNIVERSE
from marketpulse.contracts.market import CandleInterval
from marketpulse.observability.market_data import MarketDataMetrics


def test_market_data_metrics_render_quality_values() -> None:
    report = CandleQualityReport(
        instrument=INITIAL_UNIVERSE[0],
        interval=CandleInterval.ONE_HOUR,
        checked_at=datetime(2026, 1, 1, tzinfo=UTC),
        record_count=1,
        expected_count=2,
        freshness_seconds=12,
        issues=(
            QualityIssue(
                code="MISSING_CANDLE",
                severity=QualitySeverity.WARNING,
                message="missing",
            ),
        ),
    )
    metrics = MarketDataMetrics()
    metrics.observe(report, source="binance-usdm")

    rendered = metrics.render()
    assert b"marketpulse_candle_freshness_seconds" in rendered
    assert b" 12.0" in rendered
    assert b"marketpulse_missing_candles" in rendered
