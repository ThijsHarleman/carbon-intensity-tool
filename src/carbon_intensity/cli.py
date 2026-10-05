"""Command-line interface for the Carbon Intensity tool."""

from argparse import ArgumentParser
from datetime import date

from carbon_intensity.models import DateRange

def parse_args() -> DateRange:
    """Parse command-line arguments into a date range."""
    parser = ArgumentParser(
        description=(
            "Retrieve and process UK electricity generation data "
            "for an inclusive date range."
        )
    )

    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--end-date",
        required=True,
        help="End date in YYYY-MM-DD format.",
    )

    args = parser.parse_args()

    try:
        start_date = date.fromisoformat(args.start_date)
        end_date = date.fromisoformat(args.end_date)
    except ValueError:
        parser.error("Dates must use YYYY-MM-DD format.")

    try:
        return DateRange(
            start=start_date,
            end=end_date,
        )
    except ValueError as exc:
        parser.error(str(exc))
