"""Numerically stable probabilistic and point-forecast metrics."""

import math
from collections.abc import Sequence
from dataclasses import dataclass

from marketpulse.contracts.datasets import ForecastEvaluationRow


@dataclass(frozen=True)
class ForecastMetrics:
    """Aggregate metrics for P10/P50/P90 forecasts."""

    count: int
    pinball_p10: float
    pinball_p50: float
    pinball_p90: float
    interval_coverage: float
    interval_width: float
    mae: float
    rmse: float


def pinball_loss(actual: float, prediction: float, quantile: float) -> float:
    """Return asymmetric quantile loss under the standard check function."""
    if not 0 < quantile < 1:
        raise ValueError("quantile must be strictly between zero and one")
    error = actual - prediction
    return max(quantile * error, (quantile - 1) * error)


def evaluate_forecasts(evaluations: Sequence[ForecastEvaluationRow]) -> ForecastMetrics:
    """Aggregate losses, empirical interval coverage, and point errors."""
    if not evaluations:
        raise ValueError("forecast evaluation requires at least one row")
    count = len(evaluations)
    p10_loss = math.fsum(pinball_loss(row.actual, row.forecast.p10, 0.10) for row in evaluations)
    p50_loss = math.fsum(pinball_loss(row.actual, row.forecast.p50, 0.50) for row in evaluations)
    p90_loss = math.fsum(pinball_loss(row.actual, row.forecast.p90, 0.90) for row in evaluations)
    errors = [row.actual - row.forecast.p50 for row in evaluations]
    return ForecastMetrics(
        count=count,
        pinball_p10=p10_loss / count,
        pinball_p50=p50_loss / count,
        pinball_p90=p90_loss / count,
        interval_coverage=sum(
            row.forecast.p10 <= row.actual <= row.forecast.p90 for row in evaluations
        )
        / count,
        interval_width=math.fsum(row.forecast.p90 - row.forecast.p10 for row in evaluations)
        / count,
        mae=math.fsum(abs(error) for error in errors) / count,
        rmse=math.sqrt(math.fsum(error * error for error in errors) / count),
    )
