from datetime import UTC, datetime, timedelta

import pytest

from marketpulse.contracts.datasets import ForecastEvaluationRow
from marketpulse.contracts.forecasts import ForecastTarget, QuantileForecast
from marketpulse.contracts.instruments import INITIAL_UNIVERSE
from marketpulse.metrics.forecast import evaluate_forecasts, pinball_loss


def evaluation(actual: float, *, index: int = 0) -> ForecastEvaluationRow:
    generated = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=index)
    return ForecastEvaluationRow(
        fold=0,
        forecast=QuantileForecast(
            instrument=INITIAL_UNIVERSE[0],
            generated_at=generated,
            horizon_hours=24,
            target=ForecastTarget.FORWARD_LOG_RETURN_24H,
            model_version="test-v1",
            regime="all",
            p10=-0.1,
            p50=0.0,
            p90=0.1,
        ),
        actual=actual,
        target_computed_at=generated + timedelta(days=1),
    )


def test_forecast_metrics_match_known_values() -> None:
    metrics = evaluate_forecasts([evaluation(-0.05), evaluation(0.05, index=1)])

    assert metrics.count == 2
    assert metrics.interval_coverage == 1.0
    assert metrics.interval_width == pytest.approx(0.2)
    assert metrics.mae == pytest.approx(0.05)
    assert metrics.rmse == pytest.approx(0.05)
    assert pinball_loss(1.0, 0.0, 0.5) == 0.5


def test_forecast_metrics_reject_empty_and_invalid_quantile() -> None:
    with pytest.raises(ValueError, match="at least one"):
        evaluate_forecasts([])
    with pytest.raises(ValueError, match="strictly"):
        pinball_loss(1.0, 0.0, 1.0)
