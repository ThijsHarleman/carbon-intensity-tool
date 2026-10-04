"""Processing of electricity generation data."""

from dataclasses import dataclass
from datetime import datetime

from carbon_intensity.models import FuelType, GenerationMixPeriod

@dataclass(frozen=True)
class ProcessedGenerationPeriod:
    """Calculated generation metrics for a single time interval."""

    start: datetime
    end: datetime
    renewable_percentage: float
    solar_percentage_of_total: float
    solar_percentage_of_renewables: float

class GenerationProcessor:
    """Calculate renewable and solar generation metrics."""

    def process(
        self,
        periods: list[GenerationMixPeriod],
    ) -> list[ProcessedGenerationPeriod]:
        """Process generation periods into calculated metrics."""
        return [
            self._process_period(period)
            for period in periods
        ]

    @staticmethod
    def _process_period(
        period: GenerationMixPeriod,
    ) -> ProcessedGenerationPeriod:
        """Calculate metrics for one generation period."""
        percentages = {
            share.fuel: share.percentage
            for share in period.generation_mix
        }

        renewable_percentage = sum(
            percentages.get(fuel, 0.0)
            for fuel in FuelType
        )

        solar_percentage = percentages.get(FuelType.SOLAR, 0.0)

        if renewable_percentage == 0:
            solar_percentage_of_renewables = 0.0
        else:
            solar_percentage_of_renewables = (
                solar_percentage / renewable_percentage
            ) * 100

        return ProcessedGenerationPeriod(
            start=period.start,
            end=period.end,
            renewable_percentage=renewable_percentage,
            solar_percentage_of_total=solar_percentage,
            solar_percentage_of_renewables=solar_percentage_of_renewables,
        )
