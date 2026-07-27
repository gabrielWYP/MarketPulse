from datetime import UTC, datetime, timedelta

import httpx
import pytest

from marketpulse.contracts.instruments import INITIAL_UNIVERSE
from marketpulse.ingestion.binance_usdm import BinanceUsdMClient, RetryPolicy


def exchange_info(
    symbol: str = "BTCUSDT",
    *,
    status: str = "TRADING",
    contract_type: str = "PERPETUAL",
) -> dict[str, object]:
    return {
        "symbols": [
            {
                "symbol": symbol,
                "status": status,
                "contractType": contract_type,
                "onboardDate": 1_700_000_000_000,
                "pricePrecision": 2,
                "quantityPrecision": 3,
            }
        ]
    }


def kline(open_time: datetime, price: str = "100") -> list[object]:
    start_ms = int(open_time.timestamp() * 1000)
    return [start_ms, price, "105", "95", "101", "10", start_ms + 3_600_000 - 1]


def test_get_contract_validates_live_perpetual() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=exchange_info()))
    client = httpx.Client(transport=transport, base_url="https://example.test")

    contract = BinanceUsdMClient(client=client).get_contract(INITIAL_UNIVERSE[0])

    assert contract.symbol == "BTCUSDT"
    assert contract.contract_type == "PERPETUAL"

    tradifi = httpx.Client(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json=exchange_info("QQQUSDT", contract_type="TRADIFI_PERPETUAL"),
            )
        ),
        base_url="https://example.test",
    )
    assert (
        BinanceUsdMClient(client=tradifi).get_contract(INITIAL_UNIVERSE[2]).contract_type
        == "TRADIFI_PERPETUAL"
    )


def test_get_contract_rejects_absent_or_non_trading_symbol() -> None:
    absent = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=exchange_info("ETHUSDT"))),
        base_url="https://example.test",
    )
    with pytest.raises(ValueError, match="absent"):
        BinanceUsdMClient(client=absent).get_contract(INITIAL_UNIVERSE[0])

    halted = httpx.Client(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=exchange_info(status="BREAK"))
        ),
        base_url="https://example.test",
    )
    with pytest.raises(ValueError, match="not a supported trading"):
        BinanceUsdMClient(client=halted).get_contract(INITIAL_UNIVERSE[0])


def test_fetch_closed_hourly_candles_maps_binance_boundaries() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows = [kline(start), kline(start + timedelta(hours=1), "101")]
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=rows))
    client = httpx.Client(transport=transport, base_url="https://example.test")

    candles = BinanceUsdMClient(client=client).fetch_closed_hourly_candles(
        INITIAL_UNIVERSE[0],
        start=start,
        end=start + timedelta(hours=2),
        observed_at=start + timedelta(hours=2, seconds=5),
    )

    assert len(candles) == 2
    assert candles[0].close_time == start + timedelta(hours=1)
    assert candles[1].open_time == start + timedelta(hours=1)


def test_fetch_retries_rate_limit_and_rejects_bad_ranges() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    calls = 0
    sleeps: list[float] = []

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})
        return httpx.Response(200, json=[kline(start)])

    http = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://example.test")
    client = BinanceUsdMClient(
        client=http,
        retry_policy=RetryPolicy(max_attempts=2, max_backoff_seconds=5),
        sleeper=sleeps.append,
    )
    candles = client.fetch_closed_hourly_candles(
        INITIAL_UNIVERSE[0],
        start=start,
        end=start + timedelta(hours=1),
        observed_at=start + timedelta(hours=1),
    )
    assert len(candles) == 1
    assert sleeps == [2.0]

    with pytest.raises(ValueError, match="full UTC hours"):
        client.fetch_closed_hourly_candles(
            INITIAL_UNIVERSE[0],
            start=start + timedelta(minutes=1),
            end=start + timedelta(hours=1),
        )
