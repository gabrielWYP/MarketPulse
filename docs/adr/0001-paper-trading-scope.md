# ADR 0001: Paper-trading-only execution boundary

- Status: Accepted
- Date: 2026-07-27

## Context

MarketPulse must demonstrate forecasting, MLOps lifecycle, and economic
evaluation without creating an uncontrolled path to capital deployment.

## Decision

The current product supports historical backtesting, simulated execution, and
paper/shadow trading only. It will not submit, modify, or cancel real orders.
Configuration uses literal types so `real_order_execution_enabled=true` fails
validation rather than silently changing runtime behavior.

## Consequences

- Public market data requires no Binance API key.
- Paper credentials, if introduced, remain outside Git.
- Real execution requires a future ADR, threat model, account isolation, loss
  limits, kill switch, audit trail, and explicit human approval.
