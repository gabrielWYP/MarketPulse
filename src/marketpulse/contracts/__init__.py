"""Versioned data contracts shared across MarketPulse modules."""

from marketpulse.contracts.features import FeatureSnapshot
from marketpulse.contracts.forecasts import ForecastTarget, QuantileForecast, RealizedTarget
from marketpulse.contracts.instruments import INITIAL_UNIVERSE, InstrumentId, InstrumentType, Venue
from marketpulse.contracts.market import Candle, CandleInterval
from marketpulse.contracts.news import NewsItem

__all__ = [
    "INITIAL_UNIVERSE",
    "Candle",
    "CandleInterval",
    "FeatureSnapshot",
    "ForecastTarget",
    "InstrumentId",
    "InstrumentType",
    "NewsItem",
    "QuantileForecast",
    "RealizedTarget",
    "Venue",
]
