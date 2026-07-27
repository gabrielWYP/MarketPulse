import json

from marketpulse.cli import main
from marketpulse.observability import configure_logging


def test_cli_emits_structured_paper_trading_readiness(capsys: object) -> None:
    configure_logging("INFO")
    main()

    captured = capsys.readouterr()  # type: ignore[attr-defined]
    event = json.loads(captured.out.strip().splitlines()[-1])
    assert event["event"] == "marketpulse_ready"
    assert event["paper_trading_enabled"] is True
    assert event["real_order_execution_enabled"] is False
