"""Typed application configuration with a hard paper-trading boundary."""

from enum import StrEnum
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported runtime environments."""

    LOCAL = "local"
    CI = "ci"
    DEV = "dev"
    PROD = "prod"


class LogLevel(StrEnum):
    """Supported structured logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """Resolve non-secret settings from `MARKETPULSE_` environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="MARKETPULSE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    environment: Environment = Environment.LOCAL
    log_level: LogLevel = LogLevel.INFO
    paper_trading_enabled: Literal[True] = True
    real_order_execution_enabled: Literal[False] = False
