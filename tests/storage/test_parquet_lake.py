from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from marketpulse.storage.blobs import LocalBlobStore
from marketpulse.storage.parquet_lake import RawCandleLake
from tests.factories import make_hourly_candles


def test_parquet_lake_round_trip_and_idempotent_manifest(tmp_path: Path) -> None:
    lake = RawCandleLake(LocalBlobStore(tmp_path))
    candles = make_hourly_candles(4)
    created_at = datetime(2026, 1, 2, tzinfo=UTC)

    first = lake.persist(
        candles,
        exchange_contract_type="PERPETUAL",
        created_at=created_at,
    )
    replay = lake.persist(
        candles,
        exchange_contract_type="PERPETUAL",
        created_at=created_at + timedelta(days=1),
    )

    assert first == replay
    assert first[0].record_count == 4
    assert first[0].exchange_contract_type == "PERPETUAL"
    assert lake.read(first[0]) == candles
    assert first[0].object_path.endswith(".parquet")


def test_parquet_lake_partitions_by_utc_date(tmp_path: Path) -> None:
    start = datetime(2026, 1, 1, 22, tzinfo=UTC)
    manifests = RawCandleLake(LocalBlobStore(tmp_path)).persist(
        make_hourly_candles(4, start=start),
        exchange_contract_type="PERPETUAL",
        created_at=start + timedelta(days=1),
    )

    assert [manifest.partition_date for manifest in manifests] == ["2026-01-01", "2026-01-02"]
    assert [manifest.record_count for manifest in manifests] == [2, 2]


def test_local_blob_store_rejects_conflicts_and_traversal(tmp_path: Path) -> None:
    store = LocalBlobStore(tmp_path)
    store.write_bytes("safe/object.bin", b"one", content_type="application/octet-stream")
    store.write_bytes("safe/object.bin", b"one", content_type="application/octet-stream")

    with pytest.raises(ValueError, match="conflict"):
        store.write_bytes("safe/object.bin", b"two", content_type="application/octet-stream")
    with pytest.raises(ValueError, match="escapes"):
        store.exists("../outside")


def test_lake_rejects_empty_collection(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        RawCandleLake(LocalBlobStore(tmp_path)).persist(
            [],
            exchange_contract_type="PERPETUAL",
        )
