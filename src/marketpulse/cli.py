"""MarketPulse command-line entrypoint."""

import structlog

from marketpulse.config import Settings
from marketpulse.observability.logging import configure_logging


def main() -> None:
    """Validate configuration and emit a structured readiness event."""
    settings = Settings()
    configure_logging(settings.log_level.value)
    logger = structlog.get_logger(__name__)
    logger.info(
        "marketpulse_ready",
        environment=settings.environment.value,
        paper_trading_enabled=settings.paper_trading_enabled,
        real_order_execution_enabled=settings.real_order_execution_enabled,
    )


if __name__ == "__main__":
    main()
