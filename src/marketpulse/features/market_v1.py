"""Deterministic price/volume features built from closed hourly windows."""

import math
from collections.abc import Sequence
from statistics import fmean, pstdev

from marketpulse.contracts.features import FeatureSnapshot
from marketpulse.contracts.market import Candle
from marketpulse.targets.realized_volatility import log_realized_variance

_MIN_HISTORY = 24


def build_market_v1_features(candles: Sequence[Candle]) -> tuple[FeatureSnapshot, ...]:
    """Build trailing-only market features after 24 complete hourly returns."""
    ordered = tuple(sorted(candles, key=lambda candle: candle.open_time))
    _validate_series(ordered)
    snapshots: list[FeatureSnapshot] = []
    for index in range(_MIN_HISTORY, len(ordered)):
        window = ordered[index - _MIN_HISTORY : index + 1]
        current = window[-1]
        closes = [float(candle.close) for candle in window]
        volumes = [float(candle.volume) for candle in window[1:]]
        volume_std = pstdev(volumes)
        volume_zscore = 0.0 if volume_std == 0 else (volumes[-1] - fmean(volumes)) / volume_std
        availability_time = max(candle.available_at for candle in window)
        parkinson_variance = fmean(
            math.log(float(candle.high) / float(candle.low)) ** 2 / (4 * math.log(2))
            for candle in window[1:]
        )
        snapshots.append(
            FeatureSnapshot(
                instrument=current.instrument,
                feature_time=current.close_time,
                availability_time=availability_time,
                prediction_time=availability_time,
                feature_set_version="market_v1",
                features={
                    "log_return_1h": math.log(closes[-1] / closes[-2]),
                    "log_return_6h": math.log(closes[-1] / closes[-7]),
                    "log_return_24h": math.log(closes[-1] / closes[0]),
                    "log_realized_variance_24h": log_realized_variance(closes),
                    "parkinson_variance_24h": parkinson_variance,
                    "volume_zscore_24h": volume_zscore,
                    "range_fraction_1h": (float(current.high) - float(current.low))
                    / float(current.close),
                },
            )
        )
    return tuple(snapshots)


def _validate_series(candles: Sequence[Candle]) -> None:
    if len(candles) <= _MIN_HISTORY:
        raise ValueError("market_v1 requires at least 25 hourly candles")
    first = candles[0]
    if any(
        candle.instrument != first.instrument or candle.interval is not first.interval
        for candle in candles
    ):
        raise ValueError("feature input must contain one instrument and interval")
    if len({candle.open_time for candle in candles}) != len(candles):
        raise ValueError("feature input cannot contain duplicate open_time values")
