# ADR 0003: Continuous forecasting targets

- Status: Accepted
- Date: 2026-07-27

## Context

A volatility forecast does not determine long or short direction. A forced
binary target also ignores the economically important no-trade decision and
couples ground truth to a mutable cost assumption.

## Decision

The canonical targets are continuous:

1. `log_realized_variance_24h`, derived from 24 closed one-hour returns:

   `log(sum(r_i^2) + epsilon)`

2. `forward_log_return_{1h,4h,24h}`, calculated from an executable entry price
   after prediction time to the corresponding executable exit price.

Volatility and return models are trained separately first. Quantile regression
uses pinball loss because it estimates conditional quantiles without assuming
Gaussian residuals. `short / flat / long` labels are derived by a versioned,
cost-aware policy and are not stored as the canonical market outcome.

## Consequences

- Every target is materialized only after its complete horizon.
- Walk-forward splits purge overlapping label horizons.
- Classification metrics are secondary to calibrated distributions and net
  economic performance.
