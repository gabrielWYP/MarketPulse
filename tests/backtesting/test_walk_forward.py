import math
from datetime import UTC, datetime, timedelta

import pytest

from marketpulse.backtesting.walk_forward import (
    WalkForwardConfig,
    build_folds,
    run_walk_forward,
)
from marketpulse.baselines.naive import BaselineKind, forecast_baseline
from marketpulse.contracts.datasets import TrainingRow
from marketpulse.contracts.forecasts import ForecastTarget
from marketpulse.contracts.instruments import INITIAL_UNIVERSE


def training_rows(count: int = 100) -> tuple[TrainingRow, ...]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return tuple(
        TrainingRow(
            instrument=INITIAL_UNIVERSE[0],
            prediction_time=start + timedelta(hours=index),
            feature_time=start + timedelta(hours=index),
            feature_availability_time=start + timedelta(hours=index),
            target_computed_at=start + timedelta(hours=index + 24),
            target=ForecastTarget.FORWARD_LOG_RETURN_24H,
            features={"x": float(index)},
            value=0.01 * math.sin(index / 5),
        )
        for index in range(count)
    )


def test_build_folds_applies_purge_and_expands_training() -> None:
    config = WalkForwardConfig(
        minimum_train_rows=40,
        test_rows=10,
        step_rows=10,
        purge_rows=4,
        rolling_window=20,
    )
    folds = build_folds(80, config)

    assert len(folds) == 3
    assert folds[0].train_end == 40
    assert folds[0].test_start == 44
    assert folds[1].train_end == 50


@pytest.mark.parametrize("kind", list(BaselineKind))
def test_walk_forward_produces_ordered_out_of_sample_forecasts(kind: BaselineKind) -> None:
    config = WalkForwardConfig(40, 10, 10, 4, 20)
    evaluations = run_walk_forward(training_rows(), kind=kind, config=config)

    assert len(evaluations) == 50
    assert all(row.forecast.p10 <= row.forecast.p50 <= row.forecast.p90 for row in evaluations)
    assert all(row.forecast.generated_at < row.target_computed_at for row in evaluations)


def test_baseline_rejects_unavailable_history_and_invalid_window() -> None:
    rows = training_rows(30)
    early_test = rows[1]
    with pytest.raises(ValueError, match="available"):
        forecast_baseline(rows[:1], early_test, kind=BaselineKind.PERSISTENCE)
    with pytest.raises(ValueError, match="at least two"):
        forecast_baseline(rows[:25], rows[29], kind=BaselineKind.PERSISTENCE, rolling_window=1)


def test_walk_forward_config_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError, match="positive"):
        WalkForwardConfig(minimum_train_rows=0)
    with pytest.raises(ValueError, match="purge"):
        WalkForwardConfig(purge_rows=-1)
