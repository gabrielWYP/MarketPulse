"""Runtime factories that keep infrastructure concerns out of domain modules."""

from minio import Minio

from marketpulse.config import RawStorageBackend, Settings
from marketpulse.storage.blobs import BlobStore, LocalBlobStore, MinioBlobStore


def build_blob_store(settings: Settings) -> BlobStore:
    """Create the configured local or MinIO raw-object backend."""
    if settings.raw_storage_backend is RawStorageBackend.LOCAL:
        return LocalBlobStore(settings.raw_storage_root)
    if settings.minio_access_key is None or settings.minio_secret_key is None:
        raise ValueError("MinIO credentials are required")
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key.get_secret_value(),
        secret_key=settings.minio_secret_key.get_secret_value(),
        secure=settings.minio_secure,
    )
    return MinioBlobStore(client, settings.minio_bucket)
