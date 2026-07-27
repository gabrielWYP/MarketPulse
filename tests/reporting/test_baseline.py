import pytest

from marketpulse.metrics.forecast import ForecastMetrics
from marketpulse.reporting.baseline import (
    BaselineResult,
    render_baseline_report,
    render_forecast_svg,
    result_as_dict,
)
from tests.metrics.test_forecast import evaluation


def result() -> BaselineResult:
    return BaselineResult(
        instrument="BINANCE:USD_M_PERPETUAL:BTCUSDT",
        target="forward_log_return_24h",
        model="persistence",
        forecast_metrics=ForecastMetrics(1, 0.1, 0.1, 0.1, 1.0, 0.2, 0.1, 0.1),
    )


def test_report_and_svg_are_reproducible() -> None:
    report = render_baseline_report([result()], dataset_sha256="a" * 64)
    svg = render_forecast_svg([evaluation(0.1), evaluation(-0.05, index=1)], title="BTC <test>")

    assert "Dataset SHA-256" in report
    assert "BTCUSDT" in report
    assert "&lt;test&gt;" in svg
    assert "polyline" in svg
    assert result_as_dict(result())["model"] == "persistence"


def test_report_and_svg_reject_missing_or_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="at least one"):
        render_baseline_report([], dataset_sha256="a" * 64)
    with pytest.raises(ValueError, match="at least one"):
        render_forecast_svg([], title="empty")
    with pytest.raises(ValueError, match="too small"):
        render_forecast_svg([evaluation(0.1)], title="small", width=100)
