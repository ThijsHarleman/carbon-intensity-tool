"""Models representing responses from the Carbon Intensity API."""

from dataclasses import dataclass

@dataclass(frozen=True)
class ApiGenerationMixEntry:
    """A single fuel contribution returned by the API."""

    fuel: str
    percentage: float

@dataclass(frozen=True)
class ApiGenerationMixPeriod:
    """A generation-mix interval returned by the API."""

    start: str
    end: str
    generation_mix: tuple[ApiGenerationMixEntry, ...]
