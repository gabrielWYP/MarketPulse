from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

import marketpulse.runtime as runtime
from marketpulse.config import RawStorageBackend, Settings
from marketpulse.runtime import build_blob_store
from marketpulse.storage.blobs import LocalBlobStore


def test_runtime_builds_local_store(tmp_path: Path) -> None:
    settings = Settings(_env_file=None, raw_storage_root=tmp_path)
    assert isinstance(build_blob_store(settings), LocalBlobStore)


def test_minio_settings_require_non_empty_credentials() -> None:
    with pytest.raises(ValidationError, match="requires both"):
        Settings(_env_file=None, raw_storage_backend=RawStorageBackend.MINIO)
    with pytest.raises(ValidationError, match="cannot be empty"):
        Settings(
            _env_file=None,
            raw_storage_backend=RawStorageBackend.MINIO,
            minio_access_key="",
            minio_secret_key="",
        )


def test_runtime_builds_minio_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    monkeypatch.setattr(runtime, "Minio", lambda *args, **kwargs: sentinel)
    monkeypatch.setattr(runtime, "MinioBlobStore", lambda client, bucket: (client, bucket))
    settings = Settings(
        _env_file=None,
        raw_storage_backend=RawStorageBackend.MINIO,
        minio_access_key="access",
        minio_secret_key="secret",
        minio_bucket="raw",
    )
    built = cast(tuple[object, str], build_blob_store(settings))
    assert built == (sentinel, "raw")
