"""Distribution-aware return and realized-variance target primitives."""

import math
from collections.abc import Sequence
from datetime import timedelta
from itertools import pairwise

from marketpulse.contracts.forecasts import ForecastTarget, RealizedTarget
from marketpulse.contracts.market import Candle


def _validate_prices(prices: Sequence[float]) -> None:
    """Validate that a price path can produce at least one log return."""
    if len(prices) < 2:
        raise ValueError("at least two prices are required")
    if any(not math.isfinite(price) or price <= 0 for price in prices):
        raise ValueError("prices must be finite and strictly positive")


def forward_log_return(prices: Sequence[float]) -> float:
    """Calculate the terminal log return across an executable price path."""
    _validate_prices(prices)
    return math.log(prices[-1] / prices[0])


def realized_variance(prices: Sequence[float]) -> float:
    """Calculate unannualized realized variance as the sum of squared log returns."""
    _validate_prices(prices)
    returns = (math.log(current / previous) for previous, current in pairwise(prices))
    return math.fsum(log_return * log_return for log_return in returns)


def log_realized_variance(prices: Sequence[float], *, epsilon: float = 1e-12) -> float:
    """Calculate a stable positive-target transform for quantile forecasting."""
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be finite and strictly positive")
    return math.log(realized_variance(prices) + epsilon)


def build_realized_targets(
    candles: Sequence[Candle], *, horizon_hours: int = 24
) -> tuple[RealizedTarget, ...]:
    """Materialize forward return and variance only after each full horizon."""
    if horizon_hours != 24:
        raise ValueError("C1 target contract currently supports only a 24-hour horizon")
    ordered = tuple(sorted(candles, key=lambda candle: candle.open_time))
    if len(ordered) <= horizon_hours:
        raise ValueError("not enough candles to build the requested horizon")
    first = ordered[0]
    if any(
        candle.instrument != first.instrument or candle.interval is not first.interval
        for candle in ordered
    ):
        raise ValueError("target input must contain one instrument and interval")
    targets: list[RealizedTarget] = []
    for index in range(len(ordered) - horizon_hours):
        start = ordered[index]
        horizon = ordered[index : index + horizon_hours + 1]
        end = horizon[-1]
        if end.close_time - start.close_time != timedelta(hours=horizon_hours):
            continue
        prices = [float(candle.close) for candle in horizon]
        computed_at = max(end.close_time, *(candle.available_at for candle in horizon))
        targets.extend(
            (
                RealizedTarget(
                    instrument=start.instrument,
                    target=ForecastTarget.FORWARD_LOG_RETURN_24H,
                    target_start=start.close_time,
                    target_end=end.close_time,
                    computed_at=computed_at,
                    value=forward_log_return(prices),
                ),
                RealizedTarget(
                    instrument=start.instrument,
                    target=ForecastTarget.LOG_REALIZED_VARIANCE_24H,
                    target_start=start.close_time,
                    target_end=end.close_time,
                    computed_at=computed_at,
                    value=log_realized_variance(prices),
                ),
            )
        )
    return tuple(targets)
