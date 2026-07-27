from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

from marketpulse.backtesting.walk_forward import WalkForwardConfig
from marketpulse.contracts.instruments import INITIAL_UNIVERSE
from marketpulse.ingestion.binance_usdm import BinanceUsdMClient
from marketpulse.pipelines.c1 import C1Pipeline
from marketpulse.storage.blobs import LocalBlobStore
from marketpulse.storage.parquet_lake import RawCandleLake
from tests.factories import make_hourly_candles
from tests.ingestion.test_binance_usdm import exchange_info, kline


def test_pipeline_backfill_validates_persists_and_observes(tmp_path: Path) -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("exchangeInfo"):
            return httpx.Response(200, json=exchange_info())
        return httpx.Response(200, json=[kline(start), kline(start + timedelta(hours=1))])

    http = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://example.test")
    pipeline = C1Pipeline(
        BinanceUsdMClient(client=http, clock=lambda: start + timedelta(hours=3)),
        RawCandleLake(LocalBlobStore(tmp_path)),
    )

    result = pipeline.backfill(
        INITIAL_UNIVERSE[0],
        start=start,
        end=start + timedelta(hours=2),
    )

    assert len(result.candles) == 2
    assert result.quality.error_count == 0
    assert len(result.manifests) == 1
    assert (
        b'marketpulse_missing_candles{instrument="BINANCE:USD_M_PERPETUAL:BTCUSDT"'
        in pipeline.metrics.render()
    )


def test_pipeline_generates_baseline_report() -> None:
    candles = make_hourly_candles(220)
    dummy_http = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(500)),
        base_url="https://example.test",
    )
    pipeline = C1Pipeline(
        BinanceUsdMClient(client=dummy_http),
        RawCandleLake(LocalBlobStore(Path("/tmp/marketpulse-unused-test-store"))),
    )

    experiment = pipeline.run_baselines(
        candles,
        cutoff=candles[-1].ingested_at,
        walk_forward=WalkForwardConfig(60, 24, 24, 24, 48),
        round_trip_cost_bps=10,
    )

    assert len(experiment.dataset_manifests) == 2
    assert len(experiment.results) == 4
    assert "C1 baseline report" in experiment.report_markdown
    assert "persistence" in experiment.report_markdown
