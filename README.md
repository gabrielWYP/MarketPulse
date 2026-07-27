# MarketPulse

MarketPulse is a local-first MLOps platform for probabilistic forecasting and
paper-trading evaluation across heterogeneous financial instruments.

The initial universe is:

- `BINANCE:USD_M_PERPETUAL:BTCUSDT`
- `BINANCE:USD_M_PERPETUAL:ETHUSDT`
- `BINANCE:USD_M_PERPETUAL:QQQUSDT`

The MVP forecasts realized volatility and compares reproducible baselines with
quantile models. A separate research layer evaluates cost-aware
`short / flat / long` policies using out-of-sample predictions. MarketPulse does
not place real orders.

## Quickstart

Prerequisites: Python 3.12, [uv](https://docs.astral.sh/uv/), Docker, and the
Docker Compose plugin.

```bash
uv sync --frozen --all-groups
cp .env.example .env
# Replace every <set-locally> value in .env before starting containers.
make check
uv run marketpulse
docker compose up -d
docker compose ps
```

`make check` runs Ruff, formatting validation, strict mypy, pytest with a 90%
coverage gate, secret-pattern scanning, and Compose configuration validation.

The current Compose stack provides PostgreSQL, MinIO, and MLflow. It is local
development infrastructure; no cloud credentials or Binance API keys are
needed.

## Documentation

The original Office artifacts remain local and are ignored by Git. Their
metadata-free Markdown conversions are versioned for review:

- [Business design](docs/design/business-design.md)
- [Technical design](docs/design/technical-design.md)
- [Roadmap](docs/planning/roadmap.md)
- [Executable backlog](docs/planning/backlog.md)
- [Definition of Done](docs/planning/definition-of-done.md)
- [Risk register](docs/planning/risks.md)

Active architectural decisions live under `docs/adr/` and supersede conflicting
statements in the original design snapshots.

## Security boundary

Secrets must never be committed. Local values belong in ignored `.env` files;
deployment credentials belong in GitHub Actions Secrets or a cloud secret
manager. Public market-data ingestion will not require a Binance API key.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
