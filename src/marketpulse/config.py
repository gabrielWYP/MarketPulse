"""Typed application configuration with a hard paper-trading boundary."""

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
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


class RawStorageBackend(StrEnum):
    """Supported immutable raw storage implementations."""

    LOCAL = "local"
    MINIO = "minio"


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
    binance_usdm_base_url: str = "https://fapi.binance.com"
    raw_storage_backend: RawStorageBackend = RawStorageBackend.LOCAL
    raw_storage_root: Path = Path("data/raw")
    minio_endpoint: str = "localhost:9000"
    minio_bucket: str = "marketpulse"
    minio_secure: bool = False
    minio_access_key: SecretStr | None = Field(default=None, repr=False)
    minio_secret_key: SecretStr | None = Field(default=None, repr=False)

    @model_validator(mode="after")
    def require_minio_credentials(self) -> "Settings":
        """Require both credentials only when the MinIO backend is selected."""
        if self.raw_storage_backend is RawStorageBackend.MINIO:
            access_key = self.minio_access_key
            secret_key = self.minio_secret_key
            if access_key is None or secret_key is None:
                raise ValueError("MinIO storage requires both access and secret keys")
            if not access_key.get_secret_value() or not secret_key.get_secret_value():
                raise ValueError("MinIO credentials cannot be empty")
        return self
