"""CSV output for processed generation data."""

import csv
from datetime import datetime
from pathlib import Path

from carbon_intensity.processing.processor import ProcessedGenerationPeriod

class CsvReportWriter:
    """Write processed generation data to a CSV report."""

    FIELDNAMES = (
        "retrieved_at",
        "start",
        "end",
        "renewable_percentage",
        "solar_percentage_of_total",
        "solar_percentage_of_renewables",
    )

    def __init__(self, decimal_places: int = 2) -> None:
        """Initialise the writer with the desired percentage precision."""
        self._decimal_places = decimal_places

    def write(
        self,
        periods: list[ProcessedGenerationPeriod],
        retrieved_at: datetime,
        output_path: Path,
    ) -> None:
        """Write processed generation periods to a CSV file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self.FIELDNAMES,
            )

            writer.writeheader()

            for period in periods:
                writer.writerow(
                    {
                        "retrieved_at": retrieved_at.isoformat(),
                        "start": period.start.isoformat(),
                        "end": period.end.isoformat(),
                        "renewable_percentage": self._format_percentage(
                            period.renewable_percentage
                        ),
                        "solar_percentage_of_total": self._format_percentage(
                            period.solar_percentage_of_total
                        ),
                        "solar_percentage_of_renewables": self._format_percentage(
                            period.solar_percentage_of_renewables
                        ),
                    }
                )

    def _format_percentage(self, value: float) -> str:
        """Format a percentage for CSV output."""
        return f"{value:.{self._decimal_places}f}"
