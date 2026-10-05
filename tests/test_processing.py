from datetime import datetime, timezone

from carbon_intensity.models import (
    FuelGenerationShare,
    FuelType,
    GenerationMixPeriod,
)
from carbon_intensity.processing.processor import GenerationProcessor

def test_process_generation_period_calculates_expected_percentages() -> None:
    period = GenerationMixPeriod(
        start=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        end=datetime(2026, 3, 1, 10, 30, tzinfo=timezone.utc),
        generation_mix=(
            FuelGenerationShare(FuelType.BIOMASS, 9.0),
            FuelGenerationShare(FuelType.HYDRO, 0.8),
            FuelGenerationShare(FuelType.WIND, 49.2),
            FuelGenerationShare(FuelType.SOLAR, 10.0),
        ),
    )

    result = GenerationProcessor().process([period])

    assert len(result) == 1
    assert result[0].renewable_percentage == 69.0
    assert result[0].solar_percentage_of_total == 10.0
    assert result[0].solar_percentage_of_renewables == (
        10.0 / 69.0 * 100
    )

def test_process_generation_period_handles_zero_renewables() -> None:
    period = GenerationMixPeriod(
        start=datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc),
        end=datetime(2026, 3, 1, 0, 30, tzinfo=timezone.utc),
        generation_mix=(),
    )

    result = GenerationProcessor().process([period])

    assert result[0].renewable_percentage == 0.0
    assert result[0].solar_percentage_of_total == 0.0
    assert result[0].solar_percentage_of_renewables == 0.0
