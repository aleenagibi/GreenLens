"""
Provider Registry

Central registry containing metadata about all supported AI providers.
This serves as the single source of truth for provider capabilities.
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ProviderMetadata:
    """
    Metadata describing an AI provider.
    """

    name: str
    display_name: str
    default_model: str

    # Capability Scores (1–10)
    reasoning_score: int
    coding_score: int
    writing_score: int
    speed_score: int
    cost_score: int
    sustainability_score: int
    reliability_score: int

    # Features
    supports_streaming: bool
    supports_vision: bool


class ProviderRegistry:
    """
    Central registry for all supported AI providers.

    This registry acts as the single source of truth for
    provider metadata used throughout GreenLens.
    """

    _providers: ClassVar[dict[str, ProviderMetadata]] = {
        "openrouter": ProviderMetadata(
            name="openrouter",
            display_name="OpenRouter",
            default_model="openai/gpt-oss-20b:free",
            reasoning_score=9,
            coding_score=9,
            writing_score=9,
            speed_score=8,
            cost_score=10,
            sustainability_score=8,
            reliability_score=9,
            supports_streaming=True,
            supports_vision=False,
        ),
    }

    @classmethod
    def get_provider(cls, name: str) -> ProviderMetadata:
        """
        Return metadata for a specific provider.
        """

        provider = cls._providers.get(name.lower())

        if provider is None:
            raise ValueError(f"Unknown provider: {name}")

        return provider

    @classmethod
    def get_all(cls) -> dict[str, ProviderMetadata]:
        """
        Return all registered providers.
        """

        return cls._providers

    @classmethod
    def exists(cls, name: str) -> bool:
        """
        Check whether a provider exists.
        """

        return name.lower() in cls._providers