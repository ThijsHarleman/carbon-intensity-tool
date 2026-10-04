"""Client for retrieving generation data from the Carbon Intensity API."""

import httpx
import logging
from datetime import datetime, timedelta, timezone

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

        try:
            response = httpx.get(url, timeout=self._timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Failed to retrieve generation data: %s", exc)
            raise CarbonIntensityApiError(
                "Failed to retrieve generation data from the Carbon Intensity API."
            ) from exc

        try:
            response_data = response.json()
            return self._parse_response(response_data, date_range)
        except (KeyError, TypeError, ValueError) as exc:
            logger.error("Invalid response received from the Carbon Intensity API.")
            raise CarbonIntensityApiError(
                "The Carbon Intensity API returned an invalid response."
            ) from exc

    @staticmethod
    def _start_datetime(date_range: DateRange) -> str:
        """Convert the inclusive start date to an API timestamp."""
        start = datetime.combine(
            date_range.start,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        return start.strftime("%Y-%m-%dT%H:%MZ")

    @staticmethod
    def _end_datetime(date_range: DateRange) -> str:
        """Convert the inclusive end date to an API timestamp."""
        end = datetime.combine(
            date_range.end,
            datetime.min.time(),
            tzinfo=timezone.utc,
        ) + timedelta(days=1)
        return end.strftime("%Y-%m-%dT%H:%MZ")

    @staticmethod
    def _parse_response(
        response_data: dict,
        date_range: DateRange,
    ) -> list[GenerationMixPeriod]:
        """Convert API data into domain generation periods."""
        requested_start = datetime.combine(
            date_range.start,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        requested_end = datetime.combine(
            date_range.end,
            datetime.min.time(),
            tzinfo=timezone.utc,
        ) + timedelta(days=1)

        periods: list[GenerationMixPeriod] = []

        for period in response_data["data"]:
            start = datetime.fromisoformat(
                period["from"].replace("Z", "+00:00")
            )
            end = datetime.fromisoformat(
                period["to"].replace("Z", "+00:00")
            )

            if start < requested_start or end > requested_end:
                continue

            api_period = ApiGenerationMixPeriod(
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

            periods.append(
                CarbonIntensityClient._to_domain_model(api_period)
            )

        return periods

    @staticmethod
    def _to_domain_model(
        api_period: ApiGenerationMixPeriod,
    ) -> GenerationMixPeriod:
        """Convert an API generation period into a domain model."""
        generation_mix = tuple(
            FuelGenerationShare(
                fuel=FuelType(entry.fuel),
                percentage=entry.percentage,
            )
            for entry in api_period.generation_mix
            if entry.fuel in FuelType
        )

        return GenerationMixPeriod(
            start=datetime.fromisoformat(api_period.start.replace("Z", "+00:00")),
            end=datetime.fromisoformat(api_period.end.replace("Z", "+00:00")),
            generation_mix=generation_mix,
        )
