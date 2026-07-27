# ADR 0002: Initial instrument universe

- Status: Accepted
- Date: 2026-07-27

## Context

The original design mixed crypto spot-style names with QQQ, while economic
evaluation is intended for perpetual futures available around the clock.
bStocks are tokenized spot securities and do not share perpetual funding,
margin, or liquidation mechanics.

## Decision

The initial universe is:

- `BINANCE:USD_M_PERPETUAL:BTCUSDT`
- `BINANCE:USD_M_PERPETUAL:ETHUSDT`
- `BINANCE:USD_M_PERPETUAL:QQQUSDT`

Every stored record uses the full canonical identifier. bStocks are outside the
MVP. QQQUSDT metrics must be segmented by regular, pre-market, after-market,
overnight, weekend, and holiday regimes because its reference market is not
economically homogeneous across 24/7 trading.

Binance currently reports BTCUSDT and ETHUSDT as `PERPETUAL`, while QQQUSDT is
reported as `TRADIFI_PERPETUAL`. Both subtypes map to the canonical
`USD_M_PERPETUAL` type, and raw metadata retains the exchange subtype.

## Consequences

- Backtests use mark price, funding, spread, and rules for the actual contract.
- QQQ ETF data may be added later as an exogenous feature, never substituted for
  QQQUSDT execution data.
- Model promotion is evaluated per instrument and regime before aggregation.
