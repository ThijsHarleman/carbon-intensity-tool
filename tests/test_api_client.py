"""Tests for the Carbon Intensity API client."""

import httpx
import pytest
from datetime import date
from pytest import MonkeyPatch
from unittest.mock import MagicMock

from carbon_intensity.api.client import CarbonIntensityClient
from carbon_intensity.api.exceptions import CarbonIntensityApiError
from carbon_intensity.models import DateRange, FuelType

def test_get_generation_mix_converts_api_response_to_domain_models(
    monkeypatch: MonkeyPatch,
) -> None:
    """Test that a valid API response is converted to domain models."""
    api_response = {
        "data": [
            {
                "from": "2026-03-01T10:00Z",
                "to": "2026-03-01T10:30Z",
                "generationmix": [
                    {"fuel": "biomass", "perc": 9.0},
                    {"fuel": "hydro", "perc": 0.8},
                    {"fuel": "wind", "perc": 49.2},
                    {"fuel": "solar", "perc": 10.0},
                    {"fuel": "gas", "perc": 31.0},
                ],
            }
        ]
    }

    url = "https://api.carbonintensity.org.uk"
    response = httpx.Response(
        status_code=200,
        json=api_response,
        request=httpx.Request("GET", url),
    )

    mock_get = MagicMock(return_value=response)
    monkeypatch.setattr(httpx, "get", mock_get)

    date_range = DateRange(
        start=date(2026, 3, 1),
        end=date(2026, 3, 1),
    )

    result = CarbonIntensityClient().get_generation_mix(date_range)

    assert len(result) == 1

    period = result[0]

    assert period.start.isoformat() == "2026-03-01T10:00:00+00:00"
    assert period.end.isoformat() == "2026-03-01T10:30:00+00:00"

    assert {share.fuel for share in period.generation_mix} == {
        FuelType.BIOMASS,
        FuelType.HYDRO,
        FuelType.WIND,
        FuelType.SOLAR,
    }

    solar_share = next(
        share
        for share in period.generation_mix
        if share.fuel == FuelType.SOLAR
    )

    assert solar_share.percentage == 10.0

def test_get_generation_mix_raises_api_error_when_request_fails(
    monkeypatch: MonkeyPatch,
) -> None:
    """Test that an HTTP failure is converted to a domain exception."""
    mock_get = MagicMock(
        side_effect=httpx.ConnectError("Connection failed")
    )
    monkeypatch.setattr(httpx, "get", mock_get)

    date_range = DateRange(
        start=date(2026, 3, 1),
        end=date(2026, 3, 1),
    )

    with pytest.raises(CarbonIntensityApiError):
        CarbonIntensityClient().get_generation_mix(date_range)

def test_get_generation_mix_raises_api_error_for_malformed_response(
    monkeypatch: MonkeyPatch,
) -> None:
    """Test that malformed API data raises a domain exception."""
    api_response = {
        "data": [
            {
                "from": "2026-03-01T10:00Z",
                "to": "2026-03-01T10:30Z",
            }
        ]
    }

    url = CarbonIntensityClient.BASE_URL
    response = httpx.Response(
        status_code=200,
        json=api_response,
        request=httpx.Request("GET", url),
    )

    mock_get = MagicMock(return_value=response)
    monkeypatch.setattr(httpx, "get", mock_get)

    date_range = DateRange(
        start=date(2026, 3, 1),
        end=date(2026, 3, 1),
    )

    with pytest.raises(CarbonIntensityApiError):
        CarbonIntensityClient().get_generation_mix(date_range)
