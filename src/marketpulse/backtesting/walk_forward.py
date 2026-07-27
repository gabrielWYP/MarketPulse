"""Expanding-window backtesting with an explicit target-horizon purge."""

from collections.abc import Sequence
from dataclasses import dataclass

from marketpulse.baselines.naive import BaselineKind, forecast_baseline
from marketpulse.contracts.datasets import ForecastEvaluationRow, TrainingRow


@dataclass(frozen=True)
class WalkForwardConfig:
    """Sizes for deterministic expanding-window folds."""

    minimum_train_rows: int = 24 * 30
    test_rows: int = 24 * 7
    step_rows: int = 24 * 7
    purge_rows: int = 24
    rolling_window: int = 24 * 7

    def __post_init__(self) -> None:
        """Reject empty folds and negative purges."""
        if min(self.minimum_train_rows, self.test_rows, self.step_rows, self.rolling_window) < 1:
            raise ValueError("window sizes must be positive")
        if self.purge_rows < 0:
            raise ValueError("purge_rows cannot be negative")


@dataclass(frozen=True)
class WalkForwardFold:
    """Index boundaries for one out-of-sample fold."""

    fold: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def build_folds(row_count: int, config: WalkForwardConfig) -> tuple[WalkForwardFold, ...]:
    """Build expanding folds where train data ends before the purge gap."""
    folds: list[WalkForwardFold] = []
    test_start = config.minimum_train_rows + config.purge_rows
    fold = 0
    while test_start + config.test_rows <= row_count:
        train_end = test_start - config.purge_rows
        folds.append(
            WalkForwardFold(
                fold=fold,
                train_start=0,
                train_end=train_end,
                test_start=test_start,
                test_end=test_start + config.test_rows,
            )
        )
        fold += 1
        test_start += config.step_rows
    return tuple(folds)


def run_walk_forward(
    rows: Sequence[TrainingRow],
    *,
    kind: BaselineKind,
    config: WalkForwardConfig | None = None,
) -> tuple[ForecastEvaluationRow, ...]:
    """Generate only out-of-sample forecasts for every complete fold."""
    selected = config or WalkForwardConfig()
    ordered = tuple(sorted(rows, key=lambda row: row.prediction_time))
    evaluations: list[ForecastEvaluationRow] = []
    for fold in build_folds(len(ordered), selected):
        training = ordered[fold.train_start : fold.train_end]
        for test_row in ordered[fold.test_start : fold.test_end]:
            forecast = forecast_baseline(
                training,
                test_row,
                kind=kind,
                rolling_window=selected.rolling_window,
            )
            evaluations.append(
                ForecastEvaluationRow(
                    fold=fold.fold,
                    forecast=forecast,
                    actual=test_row.value,
                    target_computed_at=test_row.target_computed_at,
                )
            )
    return tuple(evaluations)
