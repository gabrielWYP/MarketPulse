# Local platform

The root `compose.yaml` provides the C0 local dependencies:

- PostgreSQL for metadata and the future forecast store.
- MinIO for S3-compatible local object storage.
- MLflow for experiment tracking and registry scaffolding.

Copy `.env.example` to `.env`, replace all placeholder values, and run:

```bash
docker compose up -d
docker compose ps
```

The initial MLflow service uses a persistent local SQLite backend and local
artifact volume. Integration with PostgreSQL and MinIO will be introduced only
with migration tests and an explicit ADR.
