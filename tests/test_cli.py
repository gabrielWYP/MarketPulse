import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

import marketpulse.cli as cli
from marketpulse.cli import main
from marketpulse.contracts.instruments import INITIAL_UNIVERSE
from marketpulse.observability import configure_logging
from tests.factories import make_hourly_candles


def test_cli_emits_structured_paper_trading_readiness(capsys: object) -> None:
    configure_logging("INFO")
    main()

    captured = capsys.readouterr()  # type: ignore[attr-defined]
    event = json.loads(captured.out.strip().splitlines()[-1])
    assert event["event"] == "marketpulse_ready"
    assert event["paper_trading_enabled"] is True
    assert event["real_order_execution_enabled"] is False


def test_cli_parses_only_full_utc_hours() -> None:
    assert cli._parse_utc_hour("2026-01-01T00:00:00Z") == datetime(2026, 1, 1, tzinfo=UTC)
    with pytest.raises(ValueError, match="UTC"):
        cli._parse_utc_hour("2026-01-01T00:00:00")
    with pytest.raises(ValueError, match="full UTC hours"):
        cli._parse_utc_hour("2026-01-01T00:01:00Z")


def test_verify_universe_command_emits_contract_events(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *_: object) -> None:
            pass

        def get_contract(self, instrument: object) -> SimpleNamespace:
            del instrument
            return SimpleNamespace(
                status="TRADING",
                contract_type="PERPETUAL",
                onboarded_at=datetime(2026, 1, 1, tzinfo=UTC),
            )

    monkeypatch.setattr(cli, "BinanceUsdMClient", FakeClient)
    main(["verify-universe"])

    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(events) == len(INITIAL_UNIVERSE)
    assert all(event["event"] == "contract_verified" for event in events)


def test_c1_run_writes_report_and_metrics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    candles = make_hourly_candles(2)

    class JsonArtifact:
        def model_dump(self, *, mode: str) -> dict[str, str]:
            assert mode == "json"
            return {"id": "manifest"}

        def model_dump_json(self) -> str:
            return '{"id":"evaluation"}'

    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *_: object) -> None:
            pass

    class FakeMetrics:
        def render(self) -> bytes:
            return b"metric 1\n"

    class FakePipeline:
        def __init__(self, *_: object) -> None:
            self.metrics = FakeMetrics()

        def backfill(self, *_: object, **__: object) -> SimpleNamespace:
            return SimpleNamespace(candles=candles, manifests=(object(),))

        def run_baselines(self, *_: object, **__: object) -> SimpleNamespace:
            return SimpleNamespace(
                report_markdown="# report\n",
                dataset_manifests=(JsonArtifact(),),
                evaluations=(JsonArtifact(),),
                charts=(("chart.svg", "<svg/>"),),
            )

    monkeypatch.setattr(cli, "BinanceUsdMClient", FakeClient)
    monkeypatch.setattr(cli, "C1Pipeline", FakePipeline)
    monkeypatch.setattr(cli, "build_blob_store", lambda _: object())
    main(
        [
            "c1-run",
            "--start",
            "2026-01-01T00:00:00Z",
            "--end",
            "2026-01-02T00:00:00Z",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert (tmp_path / "baseline-report.md").read_text() == "# report\n"
    assert (tmp_path / "market-data.prom").read_bytes() == b"metric 1\n"
    assert (tmp_path / "chart.svg").read_text() == "<svg/>"
    assert "manifest" in (tmp_path / "dataset-manifests.json").read_text()
    assert "evaluation" in (tmp_path / "evaluations.jsonl").read_text()
    assert "c1_complete" in capsys.readouterr().out
