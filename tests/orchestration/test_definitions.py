import importlib
from types import SimpleNamespace

import dagster as dg
import pytest

from marketpulse.orchestration.definitions import definitions, hourly_partitions


def test_dagster_definitions_expose_hourly_backfill_asset_and_job() -> None:
    keys = {key.to_user_string() for key in definitions.resolve_all_asset_keys()}
    jobs = {job.name for job in definitions.resolve_all_job_defs()}

    assert keys == {"raw_hourly_candles"}
    assert "c1_hourly_backfill" in jobs
    assert hourly_partitions.timezone == "UTC"


def test_hourly_asset_materializes_all_instruments(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("marketpulse.orchestration.definitions")

    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *_: object) -> None:
            pass

    class FakePipeline:
        def __init__(self, *_: object) -> None:
            pass

        def backfill(self, *_: object, **__: object) -> SimpleNamespace:
            return SimpleNamespace(candles=(object(),), manifests=(object(),))

    monkeypatch.setattr(module, "BinanceUsdMClient", FakeClient)
    monkeypatch.setattr(module, "C1Pipeline", FakePipeline)
    monkeypatch.setattr(module, "build_blob_store", lambda _: object())

    result = dg.materialize(
        [module.raw_hourly_candles],
        partition_key="2026-01-02-00:00",
    )
    assert result.success
