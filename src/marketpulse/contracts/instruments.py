"""Canonical financial instrument identifiers."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Venue(StrEnum):
    """Supported execution or observation venues."""

    BINANCE = "BINANCE"


class InstrumentType(StrEnum):
    """Supported financial instrument types."""

    USD_M_PERPETUAL = "USD_M_PERPETUAL"


class InstrumentId(BaseModel):
    """A canonical venue/type/symbol identifier."""

    model_config = ConfigDict(frozen=True)

    venue: Venue
    instrument_type: InstrumentType
    symbol: str = Field(pattern=r"^[A-Z0-9]{3,24}$")

    @property
    def canonical(self) -> str:
        """Return the stable identifier used in storage and lineage."""
        return f"{self.venue.value}:{self.instrument_type.value}:{self.symbol}"


INITIAL_UNIVERSE: tuple[InstrumentId, ...] = tuple(
    InstrumentId(
        venue=Venue.BINANCE,
        instrument_type=InstrumentType.USD_M_PERPETUAL,
        symbol=symbol,
    )
    for symbol in ("BTCUSDT", "ETHUSDT", "QQQUSDT")
)
