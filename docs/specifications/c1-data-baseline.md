# C1 data-to-baseline specification

## Scope

C1 implements MP-011 through MP-024 as a pipeline from public Binance USD-M
market data to immutable raw partitions, point-in-time datasets, probabilistic
baselines, and conservative paper-policy metrics.

The live `exchangeInfo` gate must confirm every configured contract before a
backfill. As of 2026-07-27, Binance reports:

| Symbol | Status | Binance contract type | Canonical MarketPulse type |
|---|---|---|---|
| BTCUSDT | TRADING | PERPETUAL | USD_M_PERPETUAL |
| ETHUSDT | TRADING | PERPETUAL | USD_M_PERPETUAL |
| QQQUSDT | TRADING | TRADIFI_PERPETUAL | USD_M_PERPETUAL |

`QQQUSDT` is therefore sourced from Binance Futures, not from bStocks or an ETF
spot adapter. The exact subtype is retained in ingestion metadata because its
microstructure and reference-market regimes differ from crypto perpetuals.

## Temporal contract

Each candle records two availability timestamps:

- `available_at`: earliest time the closed source observation could be used;
- `ingested_at`: time MarketPulse actually received or backfilled the record.

Features require `available_at <= prediction_time`. Raw replay and operational
latency use `ingested_at`. Targets materialize only when the last observation in
the full forward horizon is available. This separation prevents historical
backfills from moving every simulated prediction to the present.

## Immutable raw storage

Daily objects are partitioned by source, canonical instrument, interval, and
UTC date. Parquet uses Zstandard compression. Object identity is the SHA-256 of
stable market content excluding physical `ingested_at`; a replay with identical
source observations returns the existing manifest instead of adding duplicate
rows. Local filesystem and MinIO implement the same blob-store contract.

Blocking quality checks include duplicates, out-of-range observations, mixed
instrument batches, cadence violations, and missing expected candles. Missing
candles may be explicitly downgraded to warnings only for a documented source
calendar or maintenance interval.

## Features and targets

`market_v1` uses only closed trailing windows:

- log returns over 1, 6, and 24 hours;
- trailing 24-hour realized variance;
- Parkinson high-low variance;
- 24-hour volume z-score;
- latest candle range as a fraction of close.

For closes `P_t`, the return is `r_t = log(P_t / P_{t-1})`. Forward return is:

```text
R_(t,t+24) = log(P_(t+24) / P_t)
```

Realized variance is unannualized:

```text
RV_(t,t+24) = sum(r_(t+i)^2), i=1..24
```

The modeled volatility target is `log(RV + 1e-12)`. The log transform reduces
right skew and enforces a finite target near zero variance. No Gaussian return
assumption is required: P10/P50/P90 are evaluated directly with pinball loss.

## Walk-forward evaluation

Folds use an expanding training window and a purge at least as long as the
24-hour target horizon. Persistence and rolling-mean baselines estimate
empirical residual quantiles using only targets materialized by prediction
time. Metrics are aggregated out of sample:

- pinball loss at P10/P50/P90;
- empirical P10-P90 coverage and width;
- P50 MAE and RMSE;
- per-instrument, target, model, and fold evidence.

For forward-return forecasts, the C1 economic diagnostic takes at most one
non-overlapping 24-hour paper position. A trade requires the median forecast to
exceed configured round-trip costs and decision threshold. Reported metrics
include net return, expectancy, hit rate, profit factor, maximum drawdown,
Sharpe, exposure, turnover, and explicit cost drag. This diagnostic does not
model liquidation, funding, or hourly rebalancing yet and cannot promote a
system to real trading.

## Operational interfaces

- `marketpulse verify-universe`: validate live contracts without credentials.
- `marketpulse c1-run --start ... --end ...`: backfill, validate, persist, run
  baselines, and emit Markdown plus Prometheus artifacts.
- Dagster asset `raw_hourly_candles`: one closed UTC-hour partition for the
  configured universe.

Official references:

- [Binance USD-M exchange information](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#exchange-information)
- [Binance ETF-linked perpetual contracts](https://academy.binance.com/articles/etf-contracts-you-can-trade-on-binance-futures)
- [Dagster asset model](https://docs.dagster.io/)
