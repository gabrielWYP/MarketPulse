"""MarketPulse command-line entrypoint for readiness and C1 pipelines."""

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import structlog

from marketpulse.config import Settings
from marketpulse.contracts.instruments import INITIAL_UNIVERSE
from marketpulse.contracts.market import Candle
from marketpulse.ingestion.binance_usdm import BinanceUsdMClient
from marketpulse.observability.logging import configure_logging
from marketpulse.pipelines.c1 import C1Pipeline
from marketpulse.runtime import build_blob_store
from marketpulse.storage.parquet_lake import RawCandleLake


def main(argv: Sequence[str] = ()) -> None:
    """Execute a typed, paper-only operational command."""
    settings = Settings()
    configure_logging(settings.log_level.value)
    logger = structlog.get_logger(__name__)
    parser = _build_parser()
    args = parser.parse_args(list(argv))
    if args.command == "verify-universe":
        _verify_universe(settings, logger)
        return
    if args.command == "c1-run":
        _run_c1(settings, args, logger)
        return
    logger.info(
        "marketpulse_ready",
        environment=settings.environment.value,
        paper_trading_enabled=settings.paper_trading_enabled,
        real_order_execution_enabled=settings.real_order_execution_enabled,
    )


def run() -> None:
    """Console-script wrapper that passes real process arguments."""
    main(sys.argv[1:])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="marketpulse")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("ready", help="validate safe runtime configuration")
    subparsers.add_parser("verify-universe", help="verify live USD-M contracts")
    c1 = subparsers.add_parser("c1-run", help="backfill and evaluate the C1 baseline")
    c1.add_argument("--start", required=True, help="inclusive UTC ISO-8601 hour")
    c1.add_argument("--end", required=True, help="exclusive UTC ISO-8601 hour")
    c1.add_argument("--output-dir", default="artifacts/c1")
    c1.add_argument("--round-trip-cost-bps", type=float, default=10.0)
    return parser


def _verify_universe(settings: Settings, logger: structlog.stdlib.BoundLogger) -> None:
    with BinanceUsdMClient(base_url=settings.binance_usdm_base_url) as client:
        for instrument in INITIAL_UNIVERSE:
            contract = client.get_contract(instrument)
            logger.info(
                "contract_verified",
                instrument=instrument.canonical,
                status=contract.status,
                contract_type=contract.contract_type,
                onboarded_at=contract.onboarded_at.isoformat(),
            )


def _run_c1(
    settings: Settings, args: argparse.Namespace, logger: structlog.stdlib.BoundLogger
) -> None:
    start = _parse_utc_hour(str(args.start))
    end = _parse_utc_hour(str(args.end))
    output_dir = Path(str(args.output_dir))
    lake = RawCandleLake(build_blob_store(settings))
    all_candles: list[Candle] = []
    with BinanceUsdMClient(base_url=settings.binance_usdm_base_url) as client:
        pipeline = C1Pipeline(client, lake)
        for instrument in INITIAL_UNIVERSE:
            result = pipeline.backfill(instrument, start=start, end=end)
            all_candles.extend(result.candles)
            logger.info(
                "backfill_complete",
                instrument=instrument.canonical,
                records=len(result.candles),
                manifests=len(result.manifests),
            )
        experiment = pipeline.run_baselines(
            all_candles,
            cutoff=end,
            round_trip_cost_bps=float(args.round_trip_cost_bps),
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "baseline-report.md").write_text(experiment.report_markdown, encoding="utf-8")
        (output_dir / "market-data.prom").write_bytes(pipeline.metrics.render())
        (output_dir / "dataset-manifests.json").write_text(
            json.dumps(
                [manifest.model_dump(mode="json") for manifest in experiment.dataset_manifests],
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        (output_dir / "evaluations.jsonl").write_text(
            "\n".join(row.model_dump_json() for row in experiment.evaluations) + "\n",
            encoding="utf-8",
        )
        for name, svg in experiment.charts:
            (output_dir / name).write_text(svg, encoding="utf-8")
    logger.info(
        "c1_complete",
        output_dir=str(output_dir),
        datasets=len(experiment.dataset_manifests),
        evaluations=len(experiment.evaluations),
    )


def _parse_utc_hour(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        raise ValueError("timestamps must be timezone-aware UTC")
    if (parsed.minute, parsed.second, parsed.microsecond) != (0, 0, 0):
        raise ValueError("timestamps must align to full UTC hours")
    return parsed


if __name__ == "__main__":
    run()
