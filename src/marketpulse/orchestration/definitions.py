"""Hourly Dagster asset for validated Binance raw partitions."""

import dagster as dg

from marketpulse.config import Settings
from marketpulse.contracts.instruments import INITIAL_UNIVERSE
from marketpulse.ingestion.binance_usdm import BinanceUsdMClient
from marketpulse.pipelines.c1 import C1Pipeline
from marketpulse.runtime import build_blob_store
from marketpulse.storage.parquet_lake import RawCandleLake

hourly_partitions = dg.HourlyPartitionsDefinition(
    start_date="2026-01-01-00:00",
    timezone="UTC",
    fmt="%Y-%m-%d-%H:%M",
    end_offset=-1,
)


@dg.asset(partitions_def=hourly_partitions, group_name="c1_market_data")
def raw_hourly_candles(context: dg.AssetExecutionContext) -> dg.MaterializeResult[None]:
    """Backfill one closed UTC hour for every configured perpetual contract."""
    settings = Settings()
    window = context.partition_time_window
    lake = RawCandleLake(build_blob_store(settings))
    record_count = 0
    manifest_count = 0
    with BinanceUsdMClient(base_url=settings.binance_usdm_base_url) as client:
        pipeline = C1Pipeline(client, lake)
        for instrument in INITIAL_UNIVERSE:
            result = pipeline.backfill(instrument, start=window.start, end=window.end)
            record_count += len(result.candles)
            manifest_count += len(result.manifests)
    return dg.MaterializeResult(
        metadata={
            "record_count": record_count,
            "manifest_count": manifest_count,
            "partition_start": window.start.isoformat(),
            "partition_end": window.end.isoformat(),
        },
        value=None,
    )


c1_hourly_backfill = dg.define_asset_job(
    "c1_hourly_backfill",
    selection=dg.AssetSelection.assets(raw_hourly_candles),
)

definitions = dg.Definitions(
    assets=[raw_hourly_candles],
    jobs=[c1_hourly_backfill],
)
