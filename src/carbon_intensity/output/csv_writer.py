"""CSV output for processed generation data."""

from csv import DictWriter
from datetime import datetime
from pathlib import Path
from typing import TextIO

from carbon_intensity.output.exceptions import CsvReportError
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
        if decimal_places < 0:
            raise ValueError("Decimal places must not be negative.")

        self._decimal_places = decimal_places

    def write(
        self,
        periods: list[ProcessedGenerationPeriod],
        retrieved_at: datetime,
        output_path: Path,
    ) -> None:
        """Write processed generation periods to a CSV file."""
        try:
            self._prepare_output_directory(output_path)

            with output_path.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                self._write_csv(
                    csv_file,
                    periods,
                    retrieved_at,
                )
        except OSError as exc:
            raise CsvReportError(
                f"Unable to write CSV report to '{output_path}'."
            ) from exc

    @staticmethod
    def _prepare_output_directory(output_path: Path) -> None:
        """Create the output directory if it does not already exist."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_csv(
        self,
        csv_file: TextIO,
        periods: list[ProcessedGenerationPeriod],
        retrieved_at: datetime,
    ) -> None:
        """Write the CSV header and generation rows."""
        writer = DictWriter(
            csv_file,
            fieldnames=self.FIELDNAMES,
        )

        writer.writeheader()

        for period in periods:
            writer.writerow(
                self._period_to_row(period, retrieved_at)
            )

    def _period_to_row(
        self,
        period: ProcessedGenerationPeriod,
        retrieved_at: datetime,
    ) -> dict[str, str]:
        """Convert a processed period into a CSV row."""
        return {
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

    def _format_percentage(self, value: float) -> str:
        """Format a percentage for CSV output."""
        return f"{value:.{self._decimal_places}f}"
