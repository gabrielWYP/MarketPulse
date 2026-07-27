import pytest

from marketpulse.backtesting.trading import evaluate_non_overlapping_policy
from tests.metrics.test_forecast import evaluation


def test_trading_policy_uses_non_overlapping_positions_and_costs() -> None:
    rows = [evaluation(0.03, index=index) for index in range(4)]
    rows = [
        row.model_copy(
            update={
                "forecast": row.forecast.model_copy(update={"p10": 0.01, "p50": 0.02, "p90": 0.03})
            }
        )
        for row in rows
    ]

    metrics = evaluate_non_overlapping_policy(rows, round_trip_cost_bps=10)

    assert metrics.trade_count == 4
    assert metrics.total_net_return > 0
    assert metrics.cost_drag == pytest.approx(0.004)
    assert metrics.hit_rate == 1.0


def test_trading_policy_can_stay_flat_and_validates_costs() -> None:
    assert (
        evaluate_non_overlapping_policy([evaluation(0.01)], round_trip_cost_bps=10).trade_count == 0
    )
    with pytest.raises(ValueError, match="cannot be negative"):
        evaluate_non_overlapping_policy([], round_trip_cost_bps=-1)
