"""Public Binance USD-M Futures adapter for closed hourly candles."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from marketpulse.contracts.instruments import InstrumentId, InstrumentType, Venue
from marketpulse.contracts.market import Candle, CandleInterval

_HOUR = timedelta(hours=1)
_MAX_KLINES = 1500
_SUPPORTED_PERPETUAL_TYPES = {"PERPETUAL", "TRADIFI_PERPETUAL"}


class BinanceContract(BaseModel):
    """Relevant live exchange metadata for one USD-M perpetual contract."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(pattern=r"^[A-Z0-9]{3,24}$")
    status: str
    contract_type: str
    onboarded_at: datetime
    price_precision: int = Field(ge=0)
    quantity_precision: int = Field(ge=0)


@dataclass(frozen=True)
class RetryPolicy:
    """Bounded retry behavior for Binance throttling and transient failures."""

    max_attempts: int = 4
    default_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 30.0

    def __post_init__(self) -> None:
        """Reject retry policies that can loop forever or sleep negatively."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        if self.default_backoff_seconds < 0 or self.max_backoff_seconds < 0:
            raise ValueError("backoff values cannot be negative")


class BinanceUsdMClient:
    """Fetch current contract metadata and historical closed candles."""

    def __init__(
        self,
        *,
        base_url: str = "https://fapi.binance.com",
        client: httpx.Client | None = None,
        retry_policy: RetryPolicy | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize an injectable synchronous public-market client."""
        self._owns_client = client is None
        self._client = client or httpx.Client(base_url=base_url, timeout=20.0)
        self._retry_policy = retry_policy or RetryPolicy()
        self._sleeper = sleeper
        self._clock = clock or (lambda: datetime.now(UTC))

    def close(self) -> None:
        """Close the internally owned HTTP client."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> BinanceUsdMClient:
        """Return the client for context-manager use."""
        return self

    def __exit__(self, *_: object) -> None:
        """Close owned resources on context-manager exit."""
        self.close()

    def get_contract(self, instrument: InstrumentId) -> BinanceContract:
        """Validate that a configured instrument is a currently trading perpetual."""
        self._validate_instrument(instrument)
        payload = self._get_json("/fapi/v1/exchangeInfo")
        if not isinstance(payload, Mapping):
            raise ValueError("Binance exchangeInfo returned a non-object payload")
        symbols = payload.get("symbols")
        if not isinstance(symbols, Sequence):
            raise ValueError("Binance exchangeInfo omitted symbols")
        for raw_symbol in symbols:
            if not isinstance(raw_symbol, Mapping) or raw_symbol.get("symbol") != instrument.symbol:
                continue
            contract = BinanceContract(
                symbol=str(raw_symbol["symbol"]),
                status=str(raw_symbol["status"]),
                contract_type=str(raw_symbol["contractType"]),
                onboarded_at=_from_milliseconds(int(raw_symbol["onboardDate"])),
                price_precision=int(raw_symbol["pricePrecision"]),
                quantity_precision=int(raw_symbol["quantityPrecision"]),
            )
            if (
                contract.status != "TRADING"
                or contract.contract_type not in _SUPPORTED_PERPETUAL_TYPES
            ):
                raise ValueError(
                    f"{instrument.symbol} is not a supported trading USD-M perpetual: "
                    f"status={contract.status}, contract_type={contract.contract_type}"
                )
            return contract
        raise ValueError(f"{instrument.symbol} is absent from Binance USD-M exchangeInfo")

    def fetch_closed_hourly_candles(
        self,
        instrument: InstrumentId,
        *,
        start: datetime,
        end: datetime,
        observed_at: datetime | None = None,
    ) -> tuple[Candle, ...]:
        """Fetch `[start, end)` candles and discard any candle not yet closed."""
        self._validate_instrument(instrument)
        _validate_hour_range(start, end)
        ingestion_time = observed_at or self._clock()
        _require_utc(ingestion_time, "observed_at")
        cursor = start
        candles: list[Candle] = []
        while cursor < end:
            raw = self._get_json(
                "/fapi/v1/klines",
                params={
                    "symbol": instrument.symbol,
                    "interval": CandleInterval.ONE_HOUR.value,
                    "startTime": _to_milliseconds(cursor),
                    "endTime": _to_milliseconds(end) - 1,
                    "limit": _MAX_KLINES,
                },
            )
            if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
                raise ValueError("Binance klines returned a non-array payload")
            if not raw:
                break
            page = [
                self._parse_candle(instrument, row, ingestion_time)
                for row in raw
                if isinstance(row, Sequence) and not isinstance(row, (str, bytes))
            ]
            if not page:
                raise ValueError("Binance klines page contained no valid rows")
            for candle in page:
                if start <= candle.open_time and candle.close_time <= min(end, ingestion_time):
                    candles.append(candle)
            next_cursor = page[-1].open_time + _HOUR
            if next_cursor <= cursor:
                raise ValueError("Binance pagination did not advance")
            cursor = next_cursor
            if len(page) < _MAX_KLINES:
                break
        return tuple(
            sorted({candle.open_time: candle for candle in candles}.values(), key=_open_time)
        )

    def _get_json(self, path: str, *, params: Mapping[str, str | int] | None = None) -> Any:
        """Perform a bounded GET with Binance-aware backoff."""
        last_response: httpx.Response | None = None
        for attempt in range(self._retry_policy.max_attempts):
            try:
                response = self._client.get(path, params=params)
            except httpx.TransportError:
                if attempt + 1 == self._retry_policy.max_attempts:
                    raise
                self._sleeper(self._backoff(attempt, None))
                continue
            last_response = response
            if response.status_code not in {418, 429} and response.status_code < 500:
                response.raise_for_status()
                return response.json()
            if attempt + 1 == self._retry_policy.max_attempts:
                response.raise_for_status()
            self._sleeper(self._backoff(attempt, response.headers.get("Retry-After")))
        if last_response is not None:
            last_response.raise_for_status()
        raise RuntimeError("unreachable retry state")

    def _backoff(self, attempt: int, retry_after: str | None) -> float:
        """Resolve Retry-After or bounded exponential backoff."""
        try:
            requested = float(retry_after) if retry_after is not None else None
        except ValueError:
            requested = None
        delay = requested or self._retry_policy.default_backoff_seconds * (2**attempt)
        return min(max(delay, 0.0), self._retry_policy.max_backoff_seconds)

    @staticmethod
    def _validate_instrument(instrument: InstrumentId) -> None:
        """Reject accidental calls to another venue or instrument class."""
        if (
            instrument.venue is not Venue.BINANCE
            or instrument.instrument_type is not InstrumentType.USD_M_PERPETUAL
        ):
            raise ValueError("BinanceUsdMClient accepts only Binance USD-M perpetuals")

    @staticmethod
    def _parse_candle(
        instrument: InstrumentId, raw: Sequence[object], ingested_at: datetime
    ) -> Candle:
        """Convert one Binance kline array to the canonical closed-candle contract."""
        if len(raw) < 7:
            raise ValueError("Binance kline row is shorter than seven fields")
        open_time = _from_milliseconds(int(str(raw[0])))
        close_time = _from_milliseconds(int(str(raw[6])) + 1)
        return Candle(
            instrument=instrument,
            interval=CandleInterval.ONE_HOUR,
            open_time=open_time,
            close_time=close_time,
            open=Decimal(str(raw[1])),
            high=Decimal(str(raw[2])),
            low=Decimal(str(raw[3])),
            close=Decimal(str(raw[4])),
            volume=Decimal(str(raw[5])),
            source="binance-usdm",
            available_at=close_time,
            ingested_at=max(ingested_at, close_time),
        )


def _require_utc(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


def _validate_hour_range(start: datetime, end: datetime) -> None:
    _require_utc(start, "start")
    _require_utc(end, "end")
    if start >= end:
        raise ValueError("start must be earlier than end")
    if any((value.minute, value.second, value.microsecond) != (0, 0, 0) for value in (start, end)):
        raise ValueError("start and end must align to full UTC hours")


def _to_milliseconds(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _from_milliseconds(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=UTC)


def _open_time(candle: Candle) -> datetime:
    return candle.open_time
