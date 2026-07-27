"""Minimal blob-store abstraction for local and MinIO-backed raw data."""

from collections.abc import Iterator
from io import BytesIO
from pathlib import Path
from typing import Protocol

from minio import Minio
from minio.error import S3Error


class BlobStore(Protocol):
    """Byte-object operations required by immutable C1 storage."""

    def exists(self, path: str) -> bool:
        """Return whether an object exists."""

    def read_bytes(self, path: str) -> bytes:
        """Read an entire immutable object."""

    def write_bytes(self, path: str, payload: bytes, *, content_type: str) -> None:
        """Create or reconcile an immutable object."""


class LocalBlobStore:
    """Filesystem-backed object store for development and tests."""

    def __init__(self, root: Path) -> None:
        """Anchor all object keys beneath an explicit root directory."""
        self._root = root.resolve()

    def exists(self, path: str) -> bool:
        """Return whether a local object exists."""
        return self._resolve(path).is_file()

    def read_bytes(self, path: str) -> bytes:
        """Read an object from disk."""
        return self._resolve(path).read_bytes()

    def write_bytes(self, path: str, payload: bytes, *, content_type: str) -> None:
        """Atomically create an object and reject conflicting rewrites."""
        del content_type
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_bytes() != payload:
                raise ValueError(f"immutable object conflict at {path}")
            return
        temporary = target.with_suffix(f"{target.suffix}.tmp")
        temporary.write_bytes(payload)
        temporary.replace(target)

    def _resolve(self, path: str) -> Path:
        """Resolve a key while preventing traversal outside the configured root."""
        target = (self._root / path).resolve()
        if not target.is_relative_to(self._root):
            raise ValueError("object path escapes the configured root")
        return target


class MinioBlobStore:
    """MinIO-backed object store using one pre-created or auto-created bucket."""

    def __init__(self, client: Minio, bucket: str) -> None:
        """Initialize the backend and create the bucket when absent."""
        self._client = client
        self._bucket = bucket
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

    def exists(self, path: str) -> bool:
        """Return whether an object is present without listing the bucket."""
        try:
            self._client.stat_object(self._bucket, path)
        except S3Error as error:
            if error.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
                return False
            raise
        return True

    def read_bytes(self, path: str) -> bytes:
        """Read and close a MinIO response safely."""
        response = self._client.get_object(self._bucket, path)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def write_bytes(self, path: str, payload: bytes, *, content_type: str) -> None:
        """Create an object or verify an idempotent replay."""
        if self.exists(path):
            if self.read_bytes(path) != payload:
                raise ValueError(f"immutable object conflict at {path}")
            return
        self._client.put_object(
            self._bucket,
            path,
            BytesIO(payload),
            length=len(payload),
            content_type=content_type,
        )


def iter_bytes(chunks: Iterator[bytes]) -> bytes:
    """Join byte chunks; retained as a small testable streaming primitive."""
    return b"".join(chunks)
