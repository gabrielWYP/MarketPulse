import pytest
from pydantic import ValidationError

from marketpulse.config import Settings


def test_default_settings_enforce_paper_trading() -> None:
    settings = Settings(_env_file=None)

    assert settings.paper_trading_enabled is True
    assert settings.real_order_execution_enabled is False


def test_real_order_execution_cannot_be_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MARKETPULSE_REAL_ORDER_EXECUTION_ENABLED", "true")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
