"""Persistence and rolling-mean probabilistic baselines."""

from collections.abc import Sequence
from enum import StrEnum
from statistics import fmean

from marketpulse.contracts.datasets import TrainingRow
from marketpulse.contracts.forecasts import QuantileForecast


class BaselineKind(StrEnum):
    """C1 models that set a reproducible minimum-performance bar."""

    PERSISTENCE = "persistence"
    ROLLING_MEAN = "rolling_mean"


def forecast_baseline(
    train: Sequence[TrainingRow],
    test: TrainingRow,
    *,
    kind: BaselineKind,
    rolling_window: int = 24 * 7,
) -> QuantileForecast:
    """Forecast empirical quantiles without using any future target."""
    if not train:
        raise ValueError("baseline requires at least one training row")
    if rolling_window < 2:
        raise ValueError("rolling_window must be at least two")
    available = [row for row in train if row.target_computed_at <= test.prediction_time]
    if not available:
        raise ValueError("no training targets are available at prediction_time")
    history = available[-rolling_window:]
    values = [row.value for row in history]
    if kind is BaselineKind.PERSISTENCE:
        center = values[-1]
    elif kind is BaselineKind.ROLLING_MEAN:
        center = fmean(values)
    else:
        raise ValueError(f"unsupported baseline kind: {kind}")
    residuals = _one_step_residuals(values, kind)
    p10_residual = _quantile(residuals, 0.10)
    p50_residual = _quantile(residuals, 0.50)
    p90_residual = _quantile(residuals, 0.90)
    return QuantileForecast(
        instrument=test.instrument,
        generated_at=test.prediction_time,
        horizon_hours=24,
        target=test.target,
        model_version=f"{kind.value}-v1",
        regime="all",
        p10=center + p10_residual,
        p50=center + p50_residual,
        p90=center + p90_residual,
    )


def _one_step_residuals(values: Sequence[float], kind: BaselineKind) -> list[float]:
    if len(values) < 2:
        return [0.0]
    residuals: list[float] = []
    for index in range(1, len(values)):
        prediction = (
            values[index - 1] if kind is BaselineKind.PERSISTENCE else fmean(values[:index])
        )
        residuals.append(values[index] - prediction)
    return residuals


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction
