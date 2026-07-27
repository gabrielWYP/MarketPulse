"""Conservative non-overlapping paper-policy evaluation for return forecasts."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import timedelta
from itertools import pairwise

from marketpulse.contracts.datasets import ForecastEvaluationRow
from marketpulse.contracts.forecasts import ForecastTarget


@dataclass(frozen=True)
class TradingMetrics:
    """Economic metrics for a sequence of non-overlapping paper trades."""

    trade_count: int
    exposure: float
    total_net_return: float
    expectancy: float
    hit_rate: float
    profit_factor: float
    maximum_drawdown: float
    sharpe: float
    turnover: float
    cost_drag: float


def evaluate_non_overlapping_policy(
    evaluations: Sequence[ForecastEvaluationRow],
    *,
    round_trip_cost_bps: float,
    decision_threshold_bps: float = 0.0,
) -> TradingMetrics:
    """Trade median-sign signals at most once per forecast horizon."""
    if round_trip_cost_bps < 0 or decision_threshold_bps < 0:
        raise ValueError("costs and decision threshold cannot be negative")
    eligible = [
        row
        for row in sorted(evaluations, key=lambda item: item.forecast.generated_at)
        if row.forecast.target is ForecastTarget.FORWARD_LOG_RETURN_24H
    ]
    threshold = (round_trip_cost_bps + decision_threshold_bps) / 10_000
    cost = round_trip_cost_bps / 10_000
    next_entry_time = None
    net_returns: list[float] = []
    positions: list[int] = []
    for row in eligible:
        if next_entry_time is not None and row.forecast.generated_at < next_entry_time:
            continue
        median = row.forecast.p50
        position = 1 if median > threshold else -1 if median < -threshold else 0
        if position == 0:
            continue
        positions.append(position)
        net_returns.append(position * row.actual - cost)
        next_entry_time = row.forecast.generated_at + timedelta(hours=row.forecast.horizon_hours)
    if not net_returns:
        return TradingMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    equity = 1.0
    peak = 1.0
    maximum_drawdown = 0.0
    for net_return in net_returns:
        equity *= math.exp(net_return)
        peak = max(peak, equity)
        maximum_drawdown = max(maximum_drawdown, 1 - equity / peak)
    gains = sum(max(value, 0.0) for value in net_returns)
    losses = -sum(min(value, 0.0) for value in net_returns)
    mean = sum(net_returns) / len(net_returns)
    variance = sum((value - mean) ** 2 for value in net_returns) / len(net_returns)
    periods_per_year = 365 * 24 / eligible[0].forecast.horizon_hours
    sharpe = 0.0 if variance == 0 else mean / math.sqrt(variance) * math.sqrt(periods_per_year)
    turnover = 1.0 + sum(left != right for left, right in pairwise(positions))
    return TradingMetrics(
        trade_count=len(net_returns),
        exposure=len(net_returns) / max(len(eligible), 1),
        total_net_return=equity - 1,
        expectancy=mean,
        hit_rate=sum(value > 0 for value in net_returns) / len(net_returns),
        profit_factor=math.inf
        if losses == 0 and gains > 0
        else 0.0
        if losses == 0
        else gains / losses,
        maximum_drawdown=maximum_drawdown,
        sharpe=sharpe,
        turnover=float(turnover),
        cost_drag=len(net_returns) * cost,
    )
