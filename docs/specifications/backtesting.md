# Paper-trading backtest contract

## Event timing

1. Features include only observations whose `availability_time` is not later
   than `prediction_time`.
2. A forecast generated from a closed candle cannot execute at that candle's
   historical close.
3. Entry occurs at the first eligible quote after configured latency.
4. Target and performance records materialize only after the full horizon.

## Costs and perpetual mechanics

Net PnL includes:

- account/symbol maker or taker commission;
- observed or conservatively modeled spread and slippage;
- funding applied at each crossed funding timestamp;
- quantity and price rounding from exchange filters;
- maintenance margin, leverage brackets, and liquidation behavior.

Fee and funding snapshots are versioned inputs. Realized future funding must not
be used as a feature or decision-time cost estimate.

## Position policy

- `flat` is a valid action.
- One net position per instrument is the initial policy; hourly forecasts may
  rebalance it but may not create an accidental stack of 24 independent
  full-risk positions.
- Position size follows a configured account risk budget and explicit
  invalidation distance. Leverage is an implementation constraint, not the
  source of risk sizing.

## Evaluation

- Walk-forward only; no random split.
- Purge at least the maximum target horizon between dependent folds.
- Keep a final temporal test segment untouched by tuning.
- Report gross and net PnL, expectancy, turnover, fee/funding/slippage drag,
  Sharpe/Sortino, maximum drawdown, Calmar, CVaR, exposure, and margin usage.
- Break results down by instrument, direction, regime, and session.
- Use block bootstrap confidence intervals for overlapping returns and record
  every tested configuration to control selection bias.
