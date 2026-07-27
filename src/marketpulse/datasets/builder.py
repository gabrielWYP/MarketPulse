"""Join feature snapshots and delayed targets under an explicit cutoff."""

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from marketpulse.contracts.datasets import DatasetManifest, TrainingRow
from marketpulse.contracts.features import FeatureSnapshot
from marketpulse.contracts.forecasts import ForecastTarget, RealizedTarget


@dataclass(frozen=True)
class BuiltDataset:
    """Materialized rows paired with their deterministic lineage manifest."""

    rows: tuple[TrainingRow, ...]
    manifest: DatasetManifest


def build_training_dataset(
    features: Sequence[FeatureSnapshot],
    targets: Sequence[RealizedTarget],
    *,
    target: ForecastTarget,
    cutoff: datetime,
    dataset_version: str = "market-v1",
) -> BuiltDataset:
    """Create rows visible by `cutoff` and hash their canonical JSON form."""
    _require_utc(cutoff)
    target_by_key = {
        (item.instrument.canonical, item.target_start): item
        for item in targets
        if item.target is target and item.computed_at <= cutoff
    }
    rows: list[TrainingRow] = []
    for snapshot in sorted(features, key=lambda item: item.prediction_time):
        if snapshot.prediction_time > cutoff:
            continue
        realized = target_by_key.get((snapshot.instrument.canonical, snapshot.feature_time))
        if realized is None:
            continue
        rows.append(
            TrainingRow(
                instrument=snapshot.instrument,
                prediction_time=snapshot.prediction_time,
                feature_time=snapshot.feature_time,
                feature_availability_time=snapshot.availability_time,
                target_computed_at=realized.computed_at,
                target=target,
                features=snapshot.features,
                value=realized.value,
            )
        )
    encoded = json.dumps(
        [row.model_dump(mode="json") for row in rows],
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    manifest = DatasetManifest(
        dataset_version=dataset_version,
        dataset_sha256=sha256(encoded).hexdigest(),
        cutoff=cutoff,
        target=target,
        row_count=len(rows),
        first_prediction_time=rows[0].prediction_time if rows else None,
        last_prediction_time=rows[-1].prediction_time if rows else None,
    )
    return BuiltDataset(rows=tuple(rows), manifest=manifest)


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        raise ValueError("cutoff must be timezone-aware UTC")
