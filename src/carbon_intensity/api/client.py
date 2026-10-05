"""Client for retrieving generation data from the Carbon Intensity API."""

import httpx
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from carbon_intensity.api.exceptions import CarbonIntensityApiError
from carbon_intensity.api.models import (
    ApiGenerationMixEntry,
    ApiGenerationMixPeriod,
)
from carbon_intensity.models import (
    DateRange,
    FuelGenerationShare,
    FuelType,
    GenerationMixPeriod,
)

logger = logging.getLogger(__name__)

class CarbonIntensityClient:
    """Client for the national generation-mix API."""

    BASE_URL = "https://api.carbonintensity.org.uk"

    def __init__(self, timeout: float = 10.0) -> None:
        """Initialise the API client."""
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self._timeout = timeout

    def get_generation_mix(
        self,
        date_range: DateRange,
    ) -> list[GenerationMixPeriod]:
        """Retrieve generation-mix periods for an inclusive date range."""
        start = self._start_datetime(date_range)
        end = self._end_datetime(date_range)
        url = f"{self.BASE_URL}/generation/{start}/{end}"

        logger.info(
            "Requesting generation data from %s to %s",
            date_range.start,
            date_range.end,
        )

        response_data = self._request_data(url, date_range)

        return self._parse_response(response_data, date_range)

    def _request_data(
        self,
        url: str,
        date_range: DateRange,
    ) -> dict[str, Any]:
        """Request and decode generation data from the API."""
        try:
            response = httpx.get(url, timeout=self._timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error(
                "Failed to retrieve generation data from %s to %s: %s",
                date_range.start,
                date_range.end,
                exc,
            )
            raise CarbonIntensityApiError(
                "Failed to retrieve generation data from the Carbon Intensity API."
            ) from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            logger.error("The Carbon Intensity API returned invalid JSON.")
            raise CarbonIntensityApiError(
                "The Carbon Intensity API returned invalid JSON."
            ) from exc

        if not isinstance(response_data, dict):
            logger.error("The Carbon Intensity API returned an unexpected response type.")
            raise CarbonIntensityApiError(
                "The Carbon Intensity API returned an invalid response."
            )

        return response_data

    @staticmethod
    def _parse_response(
        response_data: dict[str, Any],
        date_range: DateRange,
    ) -> list[GenerationMixPeriod]:
        """Convert API data into domain generation periods."""
        try:
            requested_start = CarbonIntensityClient._date_range_start(
                date_range
            )
            requested_end = CarbonIntensityClient._date_range_end(
                date_range
            )

            periods: list[GenerationMixPeriod] = []

            for period in response_data["data"]:
                if not CarbonIntensityClient._period_is_in_range(
                    period,
                    requested_start,
                    requested_end,
                ):
                    continue

                api_period = CarbonIntensityClient._parse_period(period)
                periods.append(
                    CarbonIntensityClient._to_domain_model(api_period)
                )

            return periods

        except (KeyError, TypeError, ValueError) as exc:
            logger.error("The Carbon Intensity API returned an invalid response.")
            raise CarbonIntensityApiError(
                "The Carbon Intensity API returned an invalid response."
            ) from exc

    @staticmethod
    def _parse_period(
        period: dict[str, Any],
    ) -> ApiGenerationMixPeriod:
        """Convert one API response period into an API model."""
        return ApiGenerationMixPeriod(
            start=period["from"],
            end=period["to"],
            generation_mix=tuple(
                ApiGenerationMixEntry(
                    fuel=entry["fuel"],
                    percentage=entry["perc"],
                )
                for entry in period["generationmix"]
            ),
        )

    @staticmethod
    def _period_is_in_range(
        period: dict[str, Any],
        requested_start: datetime,
        requested_end: datetime,
    ) -> bool:
        """Return whether an API period falls within the requested range."""
        start = CarbonIntensityClient._parse_timestamp(period["from"])
        end = CarbonIntensityClient._parse_timestamp(period["to"])

        return start >= requested_start and end <= requested_end

    @staticmethod
    def _to_domain_model(
        api_period: ApiGenerationMixPeriod,
    ) -> GenerationMixPeriod:
        """Convert an API generation period into a domain model."""
        return GenerationMixPeriod(
            start=CarbonIntensityClient._parse_timestamp(api_period.start),
            end=CarbonIntensityClient._parse_timestamp(api_period.end),
            generation_mix=CarbonIntensityClient._to_generation_mix(
                api_period.generation_mix
            ),
        )

    @staticmethod
    def _to_generation_mix(
        entries: tuple[ApiGenerationMixEntry, ...],
    ) -> tuple[FuelGenerationShare, ...]:
        """Convert supported API fuel entries to domain models."""
        shares: list[FuelGenerationShare] = []

        for entry in entries:
            share = CarbonIntensityClient._to_fuel_generation_share(entry)

            if share is not None:
                shares.append(share)

        return tuple(shares)

    @staticmethod
    def _to_fuel_generation_share(
        entry: ApiGenerationMixEntry,
    ) -> FuelGenerationShare | None:
        """Convert an API fuel entry to a supported domain fuel."""
        if not isinstance(entry.fuel, str):
            raise ValueError("API fuel value must be a string.")

        try:
            fuel = FuelType(entry.fuel)
        except ValueError:
            return None

        return FuelGenerationShare(
            fuel=fuel,
            percentage=entry.percentage,
        )

    @staticmethod
    def _parse_timestamp(timestamp: str) -> datetime:
        """Convert an API timestamp into a timezone-aware datetime."""
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    @staticmethod
    def _start_datetime(date_range: DateRange) -> str:
        """Convert the inclusive start date to an API timestamp."""
        return CarbonIntensityClient._date_range_start(
            date_range
        ).strftime("%Y-%m-%dT%H:%MZ")

    @staticmethod
    def _end_datetime(date_range: DateRange) -> str:
        """Convert the inclusive end date to an API timestamp."""
        return CarbonIntensityClient._date_range_end(
            date_range
        ).strftime("%Y-%m-%dT%H:%MZ")

    @staticmethod
    def _date_range_start(date_range: DateRange) -> datetime:
        """Convert the inclusive start date to a UTC datetime."""
        return datetime.combine(
            date_range.start,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )

    @staticmethod
    def _date_range_end(date_range: DateRange) -> datetime:
        """Convert the inclusive end date to an exclusive UTC datetime."""
        return (
            datetime.combine(
                date_range.end,
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
            + timedelta(days=1)
        )
