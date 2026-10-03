"""Domain models for electricity generation data."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

class FuelType(StrEnum):
    """Fuel types supported by the Carbon Intensity generation API."""

    BIOMASS = "biomass"
    HYDRO = "hydro"
    WIND = "wind"
    SOLAR = "solar"

@dataclass(frozen=True)
class DateRange:
    """Inclusive date range requested by the user."""

    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("Start date must not be after end date.")

@dataclass(frozen=True)
class FuelGenerationShare:
    """Share of total electricity generation provided by one fuel type."""

    fuel: FuelType
    percentage: float

@dataclass(frozen=True)
class GenerationMixPeriod:
    """Electricity generation mix for a single time interval."""

    start: datetime
    end: datetime
    generation_mix: tuple[FuelGenerationShare, ...]
