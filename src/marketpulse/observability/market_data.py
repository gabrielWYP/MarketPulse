"""Prometheus metrics for market-data freshness and completeness."""

from prometheus_client import CollectorRegistry, Gauge, generate_latest

from marketpulse.contracts.ingestion import CandleQualityReport


class MarketDataMetrics:
    """Isolated metric registry safe for tests, jobs, and HTTP exposure."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        """Create gauges without using the process-global registry."""
        self.registry = registry or CollectorRegistry()
        labels = ("instrument", "source")
        self._freshness = Gauge(
            "marketpulse_candle_freshness_seconds",
            "Seconds since the latest closed candle",
            labels,
            registry=self.registry,
        )
        self._missing = Gauge(
            "marketpulse_missing_candles",
            "Missing candles in the last validated range",
            labels,
            registry=self.registry,
        )
        self._quality_errors = Gauge(
            "marketpulse_candle_quality_errors",
            "Blocking candle quality findings",
            labels,
            registry=self.registry,
        )

    def observe(self, report: CandleQualityReport, *, source: str) -> None:
        """Update all data-quality gauges from one deterministic report."""
        label_values = (report.instrument.canonical, source)
        missing = sum(issue.code == "MISSING_CANDLE" for issue in report.issues)
        self._freshness.labels(*label_values).set(report.freshness_seconds)
        self._missing.labels(*label_values).set(missing)
        self._quality_errors.labels(*label_values).set(report.error_count)

    def render(self) -> bytes:
        """Render the current registry in Prometheus text format."""
        return generate_latest(self.registry)
