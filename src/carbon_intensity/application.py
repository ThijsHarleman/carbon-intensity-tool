"""Application entry point for the Carbon Intensity tool."""

import logging
from datetime import date, datetime, timezone
from pathlib import Path

from carbon_intensity.api.client import CarbonIntensityClient
from carbon_intensity.api.exceptions import CarbonIntensityApiError
from carbon_intensity.logging_config import configure_logging
from carbon_intensity.models import DateRange
from carbon_intensity.output.csv_writer import CsvReportWriter
from carbon_intensity.output.exceptions import CsvReportError
from carbon_intensity.processing.processor import GenerationProcessor

logger = logging.getLogger(__name__)

def main() -> None:
    """Start the application."""
    configure_logging()

    logger.info("Carbon Intensity tool started.")

    try:
        _run_application()
    except (CarbonIntensityApiError, CsvReportError) as exc:
        logger.error("Application failed: %s", exc)

def _run_application() -> None:
    """Run the main application workflow."""
    date_range = DateRange(
        start=date(2026, 3, 1),
        end=date(2026, 3, 1),
    )

    client = CarbonIntensityClient()
    periods = client.get_generation_mix(date_range)

    if not periods:
        logger.warning(
            "No generation data was returned for %s to %s.",
            date_range.start,
            date_range.end,
        )
        return

    logger.info("Retrieved %d generation periods.", len(periods))

    processor = GenerationProcessor()
    processed_periods = processor.process(periods)

    logger.info("Processed %d generation periods.", len(processed_periods))

    if processed_periods:
        logger.info("First processed period: %s", processed_periods[0])
        logger.info("Sample daytime processed period: %s", processed_periods[20])
        logger.info("Last processed period: %s", processed_periods[-1])

    writer = CsvReportWriter()

    writer.write(
        periods=processed_periods,
        retrieved_at=datetime.now(timezone.utc),
        output_path=Path("output/generation_report.csv"),
    )

    logger.info("CSV report written to output/generation_report.csv")

if __name__ == "__main__":
    main()
