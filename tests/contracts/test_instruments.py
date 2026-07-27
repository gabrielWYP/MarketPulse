from marketpulse.contracts.instruments import INITIAL_UNIVERSE


def test_initial_universe_uses_canonical_perpetual_identifiers() -> None:
    assert [instrument.canonical for instrument in INITIAL_UNIVERSE] == [
        "BINANCE:USD_M_PERPETUAL:BTCUSDT",
        "BINANCE:USD_M_PERPETUAL:ETHUSDT",
        "BINANCE:USD_M_PERPETUAL:QQQUSDT",
    ]
