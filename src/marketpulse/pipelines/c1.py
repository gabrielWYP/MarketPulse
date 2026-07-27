"""C1 market-data-to-baseline pipeline independent from orchestration runtime."""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from marketpulse.backtesting.trading import evaluate_non_overlapping_policy
from marketpulse.backtesting.walk_forward import WalkForwardConfig, run_walk_forward
from marketpulse.baselines.naive import BaselineKind
from marketpulse.contracts.datasets import DatasetManifest, ForecastEvaluationRow
from marketpulse.contracts.forecasts import ForecastTarget
from marketpulse.contracts.ingestion import CandleQualityReport, IngestionManifest
from marketpulse.contracts.instruments import InstrumentId
from marketpulse.contracts.market import Candle
from marketpulse.datasets.builder import build_training_dataset
from marketpulse.features.market_v1 import build_market_v1_features
from marketpulse.ingestion.binance_usdm import BinanceUsdMClient
from marketpulse.metrics.forecast import evaluate_forecasts
from marketpulse.observability.market_data import MarketDataMetrics
from marketpulse.quality.candles import validate_candles
from marketpulse.reporting.baseline import (
    BaselineResult,
    render_baseline_report,
    render_forecast_svg,
)
from marketpulse.storage.parquet_lake import RawCandleLake
from marketpulse.targets.realized_volatility import build_realized_targets


@dataclass(frozen=True)
class BackfillResult:
    """Evidence emitted after one validated instrument backfill."""

    candles: tuple[Candle, ...]
    quality: CandleQualityReport
    manifests: tuple[IngestionManifest, ...]


@dataclass(frozen=True)
class BaselineExperiment:
    """All artifacts produced by one multi-instrument baseline run."""

    dataset_manifests: tuple[DatasetManifest, ...]
    evaluations: tuple[ForecastEvaluationRow, ...]
    results: tuple[BaselineResult, ...]
    report_markdown: str
    charts: tuple[tuple[str, str], ...]


class C1Pipeline:
    """Coordinate public ingestion, immutable storage, and baseline evaluation."""

    def __init__(
        self,
        client: BinanceUsdMClient,
        lake: RawCandleLake,
        metrics: MarketDataMetrics | None = None,
    ) -> None:
        """Inject all network and storage boundaries for deterministic tests."""
        self._client = client
        self._lake = lake
        self._metrics = metrics or MarketDataMetrics()

    @property
    def metrics(self) -> MarketDataMetrics:
        """Expose the isolated Prometheus registry for serving or persistence."""
        return self._metrics

    def backfill(
        self, instrument: InstrumentId, *, start: datetime, end: datetime
    ) -> BackfillResult:
        """Validate the live contract, fetch closed candles, gate quality, and persist."""
        contract = self._client.get_contract(instrument)
        candles = self._client.fetch_closed_hourly_candles(
            instrument,
            start=start,
            end=end,
        )
        report = validate_candles(
            candles,
            expected_start=start,
            expected_end=end,
            checked_at=max(end, datetime.now(UTC)),
        )
        self._metrics.observe(report, source="binance-usdm")
        manifests = self._lake.persist(
            candles,
            exchange_contract_type=contract.contract_type,
        )
        return BackfillResult(candles=candles, quality=report, manifests=manifests)

    def run_baselines(
        self,
        candles: Sequence[Candle],
        *,
        cutoff: datetime,
        walk_forward: WalkForwardConfig | None = None,
        round_trip_cost_bps: float = 10.0,
    ) -> BaselineExperiment:
        """Build point-in-time datasets and compare C1 baselines by instrument/target."""
        grouped: dict[str, list[Candle]] = defaultdict(list)
        for candle in candles:
            grouped[candle.instrument.canonical].append(candle)
        manifests: list[DatasetManifest] = []
        evaluations: list[ForecastEvaluationRow] = []
        results: list[BaselineResult] = []
        charts: list[tuple[str, str]] = []
        for instrument_candles in grouped.values():
            ordered = tuple(sorted(instrument_candles, key=lambda item: item.open_time))
            features = build_market_v1_features(ordered)
            targets = build_realized_targets(ordered)
            for target in (
                ForecastTarget.LOG_REALIZED_VARIANCE_24H,
                ForecastTarget.FORWARD_LOG_RETURN_24H,
            ):
                dataset = build_training_dataset(features, targets, target=target, cutoff=cutoff)
                manifests.append(dataset.manifest)
                for kind in BaselineKind:
                    model_evaluations = run_walk_forward(
                        dataset.rows,
                        kind=kind,
                        config=walk_forward,
                    )
                    if not model_evaluations:
                        continue
                    evaluations.extend(model_evaluations)
                    trading = (
                        evaluate_non_overlapping_policy(
                            model_evaluations,
                            round_trip_cost_bps=round_trip_cost_bps,
                        )
                        if target is ForecastTarget.FORWARD_LOG_RETURN_24H
                        else None
                    )
                    results.append(
                        BaselineResult(
                            instrument=ordered[0].instrument.canonical,
                            target=target.value,
                            model=kind.value,
                            forecast_metrics=evaluate_forecasts(model_evaluations),
                            trading_metrics=trading,
                        )
                    )
                    charts.append(
                        (
                            f"{ordered[0].instrument.symbol.lower()}-{target.value}-{kind.value}.svg",
                            render_forecast_svg(
                                model_evaluations,
                                title=(
                                    f"{ordered[0].instrument.symbol} {target.value} "
                                    f"{kind.value}: actual vs P50"
                                ),
                            ),
                        )
                    )
        if not results:
            raise ValueError("no complete walk-forward folds were produced")
        combined_hash = sha256(
            "".join(sorted(manifest.dataset_sha256 for manifest in manifests)).encode()
        ).hexdigest()
        return BaselineExperiment(
            dataset_manifests=tuple(manifests),
            evaluations=tuple(evaluations),
            results=tuple(results),
            report_markdown=render_baseline_report(results, dataset_sha256=combined_hash),
            charts=tuple(charts),
        )
