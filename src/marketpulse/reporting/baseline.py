"""Markdown and SVG artifacts for the C1 baseline experiment."""

import html
from collections.abc import Sequence
from dataclasses import asdict, dataclass

from marketpulse.backtesting.trading import TradingMetrics
from marketpulse.contracts.datasets import ForecastEvaluationRow
from marketpulse.metrics.forecast import ForecastMetrics


@dataclass(frozen=True)
class BaselineResult:
    """Metrics for one instrument/target/model combination."""

    instrument: str
    target: str
    model: str
    forecast_metrics: ForecastMetrics
    trading_metrics: TradingMetrics | None = None


def render_baseline_report(results: Sequence[BaselineResult], *, dataset_sha256: str) -> str:
    """Render a deterministic Markdown comparison table."""
    if not results:
        raise ValueError("baseline report requires at least one result")
    lines = [
        "# C1 baseline report",
        "",
        f"Dataset SHA-256: `{dataset_sha256}`",
        "",
        "| Instrument | Target | Model | N | Pinball P50 | Coverage P10-P90 | "
        "MAE | RMSE | Trades | Net return | Max DD | Hit rate | Sharpe | Cost drag |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        forecast = result.forecast_metrics
        trading = result.trading_metrics
        lines.append(
            "| "
            + " | ".join(
                (
                    result.instrument,
                    result.target,
                    result.model,
                    str(forecast.count),
                    f"{forecast.pinball_p50:.6f}",
                    f"{forecast.interval_coverage:.3f}",
                    f"{forecast.mae:.6f}",
                    f"{forecast.rmse:.6f}",
                    "N/A" if trading is None else str(trading.trade_count),
                    "N/A" if trading is None else f"{trading.total_net_return:.3%}",
                    "N/A" if trading is None else f"{trading.maximum_drawdown:.3%}",
                    "N/A" if trading is None else f"{trading.hit_rate:.3%}",
                    "N/A" if trading is None else f"{trading.sharpe:.3f}",
                    "N/A" if trading is None else f"{trading.cost_drag:.3%}",
                )
            )
            + " |"
        )
    lines.extend(
        (
            "",
            "Economic results use non-overlapping 24-hour paper positions and configured "
            "round-trip costs. They are a C1 diagnostic, not evidence for live-order readiness.",
            "",
        )
    )
    return "\n".join(lines)


def render_forecast_svg(
    evaluations: Sequence[ForecastEvaluationRow], *, title: str, width: int = 800, height: int = 280
) -> str:
    """Render a dependency-free SVG comparing realized values with P50."""
    if not evaluations:
        raise ValueError("forecast chart requires at least one evaluation")
    if width < 200 or height < 120:
        raise ValueError("chart dimensions are too small")
    actual = [row.actual for row in evaluations]
    predicted = [row.forecast.p50 for row in evaluations]
    low, high = min((*actual, *predicted)), max((*actual, *predicted))
    actual_points = _svg_points(actual, low=low, high=high, width=width, height=height)
    predicted_points = _svg_points(predicted, low=low, high=high, width=width, height=height)
    safe_title = html.escape(title)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{safe_title}">'
        f'<title>{safe_title}</title><rect width="100%" height="100%" fill="#0f172a"/>'
        f'<polyline points="{actual_points}" fill="none" stroke="#d7ff6e" stroke-width="2"/>'
        f'<polyline points="{predicted_points}" fill="none" stroke="#38bdf8" stroke-width="2"/>'
        "</svg>"
    )


def _svg_points(
    values: Sequence[float], *, low: float, high: float, width: int, height: int
) -> str:
    span = high - low or 1.0
    points = []
    for index, value in enumerate(values):
        x = 40 + index / max(len(values) - 1, 1) * (width - 60)
        y = 20 + (high - value) / span * (height - 50)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def result_as_dict(result: BaselineResult) -> dict[str, object]:
    """Return a JSON-ready metrics record for machine consumers."""
    return asdict(result)
