"""Immutable, partitioned Parquet storage for canonical candles."""

import json
from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import UTC, date, datetime
from hashlib import sha256
from typing import cast

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]

from marketpulse.contracts.ingestion import IngestionManifest
from marketpulse.contracts.market import Candle
from marketpulse.storage.blobs import BlobStore


class RawCandleLake:
    """Persist deterministic daily partitions and their lineage manifests."""

    def __init__(self, blob_store: BlobStore) -> None:
        """Bind the lake to a local or MinIO byte-object backend."""
        self._blob_store = blob_store

    def persist(
        self,
        candles: Iterable[Candle],
        *,
        exchange_contract_type: str,
        created_at: datetime | None = None,
    ) -> tuple[IngestionManifest, ...]:
        """Write one idempotent object per source/instrument/UTC date."""
        materialized = tuple(candles)
        if not materialized:
            raise ValueError("cannot persist an empty candle collection")
        grouped: dict[tuple[str, str, date], list[Candle]] = defaultdict(list)
        for candle in materialized:
            grouped[(candle.source, candle.instrument.canonical, candle.open_time.date())].append(
                candle
            )
        timestamp = created_at or datetime.now(UTC)
        manifests = [
            self._persist_partition(group, timestamp, exchange_contract_type)
            for group in grouped.values()
        ]
        return tuple(sorted(manifests, key=lambda manifest: manifest.object_path))

    def read(self, manifest: IngestionManifest) -> tuple[Candle, ...]:
        """Read a partition and verify its stable business-content digest."""
        payload = self._blob_store.read_bytes(manifest.object_path)
        table = pq.read_table(pa.BufferReader(payload))
        candles = tuple(Candle.model_validate(row) for row in table.to_pylist())
        if (
            _stable_content_hash(candles, manifest.exchange_contract_type)
            != manifest.content_sha256
        ):
            raise ValueError(f"content digest mismatch for {manifest.object_path}")
        return candles

    def _persist_partition(
        self,
        candles: Sequence[Candle],
        created_at: datetime,
        exchange_contract_type: str,
    ) -> IngestionManifest:
        ordered = tuple(sorted(candles, key=lambda candle: candle.open_time))
        _validate_homogeneous_partition(ordered)
        if not exchange_contract_type:
            raise ValueError("exchange_contract_type cannot be empty")
        content_hash = _stable_content_hash(ordered, exchange_contract_type)
        first = ordered[0]
        partition = first.open_time.date().isoformat()
        instrument_path = first.instrument.canonical.replace(":", "_")
        prefix = (
            f"market_candles/source={first.source}/instrument={instrument_path}/"
            f"interval={first.interval.value}/date={partition}"
        )
        object_path = f"{prefix}/part-{content_hash[:20]}.parquet"
        manifest_path = f"{prefix}/part-{content_hash[:20]}.manifest.json"
        manifest = IngestionManifest(
            source=first.source,
            instrument=first.instrument,
            exchange_contract_type=exchange_contract_type,
            interval=first.interval,
            partition_date=partition,
            object_path=object_path,
            content_sha256=content_hash,
            record_count=len(ordered),
            first_open_time=first.open_time,
            last_close_time=ordered[-1].close_time,
            created_at=created_at,
        )
        if self._blob_store.exists(manifest_path):
            stored = IngestionManifest.model_validate_json(
                self._blob_store.read_bytes(manifest_path)
            )
            if stored.content_sha256 != content_hash:
                raise ValueError(f"manifest conflict at {manifest_path}")
            return stored
        self._blob_store.write_bytes(
            object_path,
            _to_parquet_bytes(ordered),
            content_type="application/vnd.apache.parquet",
        )
        self._blob_store.write_bytes(
            manifest_path,
            manifest.model_dump_json(indent=2).encode(),
            content_type="application/json",
        )
        return manifest


def _to_parquet_bytes(candles: Sequence[Candle]) -> bytes:
    rows = []
    for candle in candles:
        payload = candle.model_dump(mode="json")
        payload["instrument"] = candle.instrument.model_dump(mode="json")
        rows.append(payload)
    table = pa.Table.from_pylist(rows)
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink, compression="zstd", version="2.6")
    return cast(bytes, sink.getvalue().to_pybytes())


def _stable_content_hash(candles: Sequence[Candle], exchange_contract_type: str) -> str:
    stable_rows = []
    for candle in candles:
        payload = candle.model_dump(mode="json", exclude={"ingested_at"})
        stable_rows.append(payload)
    encoded = json.dumps(
        {"exchange_contract_type": exchange_contract_type, "rows": stable_rows},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return sha256(encoded).hexdigest()


def _validate_homogeneous_partition(candles: Sequence[Candle]) -> None:
    if not candles:
        raise ValueError("partition cannot be empty")
    first = candles[0]
    expected = (first.source, first.instrument, first.interval, first.open_time.date())
    if any(
        (candle.source, candle.instrument, candle.interval, candle.open_time.date()) != expected
        for candle in candles
    ):
        raise ValueError("partition must contain one source, instrument, interval, and UTC date")
