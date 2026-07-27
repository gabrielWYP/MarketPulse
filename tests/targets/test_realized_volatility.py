import math

import pytest

from marketpulse.targets.realized_volatility import (
    forward_log_return,
    log_realized_variance,
    realized_variance,
)


def test_return_and_realized_variance_use_log_returns() -> None:
    prices = [100.0, 100.0 * math.exp(0.01), 100.0 * math.exp(0.01 - 0.02)]

    assert forward_log_return(prices) == pytest.approx(-0.01)
    assert realized_variance(prices) == pytest.approx(0.01**2 + (-0.02) ** 2)
    assert log_realized_variance(prices) == pytest.approx(math.log(0.01**2 + (-0.02) ** 2 + 1e-12))


@pytest.mark.parametrize("prices", [[], [100.0], [100.0, 0.0], [100.0, float("nan")]])
def test_target_builders_reject_invalid_paths(prices: list[float]) -> None:
    with pytest.raises(ValueError):
        realized_variance(prices)


def test_log_realized_variance_rejects_invalid_epsilon() -> None:
    with pytest.raises(ValueError, match="epsilon"):
        log_realized_variance([100.0, 101.0], epsilon=0.0)
