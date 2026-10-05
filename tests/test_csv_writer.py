"""Tests for CSV report output."""

import csv
from datetime import datetime, timezone
from pathlib import Path

from carbon_intensity.output.csv_writer import CsvReportWriter
from carbon_intensity.processing.processor import ProcessedGenerationPeriod

def test_write_creates_csv_report_with_processed_data(
    tmp_path: Path,
) -> None:
    """Test that processed generation data is written correctly."""
    periods = [
        ProcessedGenerationPeriod(
            start=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
            end=datetime(2026, 3, 1, 10, 30, tzinfo=timezone.utc),
            renewable_percentage=69.0,
            solar_percentage_of_total=10.0,
            solar_percentage_of_renewables=14.4927536232,
        )
    ]

    retrieved_at = datetime(
        2026,
        3,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )

    output_path = tmp_path / "generation_report.csv"

    CsvReportWriter(decimal_places=2).write(
        periods=periods,
        retrieved_at=retrieved_at,
        output_path=output_path,
    )

    assert output_path.exists()

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1

    assert rows[0] == {
        "retrieved_at": "2026-03-01T12:00:00+00:00",
        "start": "2026-03-01T10:00:00+00:00",
        "end": "2026-03-01T10:30:00+00:00",
        "renewable_percentage": "69.00",
        "solar_percentage_of_total": "10.00",
        "solar_percentage_of_renewables": "14.49",
    }
