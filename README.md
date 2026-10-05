# Carbon Intensity Tool
A Python tool that retrieves UK electricity generation data from the Carbon Intensity API, calculates renewable and solar generation percentages, and writes the results to a CSV report.

## Requirements
- Python 3.12+

## Setup
Create and activate a virtual environment:
    python -m venv .venv

Install the project and test dependencies:
    pip install -e ".[test]"

## Run
Run the application with an inclusive start and end date:
    python -m carbon_intensity.application --start-date 2026-03-01 --end-date 2026-03-14

Or, after installation:
    carbon-intensity --start-date 2026-03-01 --end-date 2026-03-14

Dates must use YYYY-MM-DD format, and the end date must not be earlier than the start date.

The generated report is written to:
    output/generation_report.csv

Logs are written to:
    logs/carbon_intensity.log

## Tests
Run the test suite with:
    pytest
