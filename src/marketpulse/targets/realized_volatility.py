"""Distribution-aware return and realized-variance target primitives."""

import math
from collections.abc import Sequence
from itertools import pairwise


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
