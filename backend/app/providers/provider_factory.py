"""
Provider Factory

Responsible for creating AI provider instances.
"""

from typing import ClassVar

from app.core.config import settings
from app.providers.base_provider import BaseProvider
from app.providers.openrouter_provider import OpenRouterProvider
from app.providers.provider_registry import ProviderRegistry


class ProviderFactory:
    """
    Factory responsible for creating AI provider instances.
    """

    _provider_classes: ClassVar[
        dict[str, type[BaseProvider]]
    ] = {
        "openrouter": OpenRouterProvider,
    }

    @classmethod
    def get_provider(
        cls,
        provider_name: str | None = None,
    ) -> BaseProvider:
        """
        Create a provider instance.

        If provider_name is not supplied, the default
        provider from configuration is used.
        """

        name = (
            provider_name
            or settings.DEFAULT_PROVIDER
        ).lower()

        if not ProviderRegistry.exists(name):
            raise ValueError(
                f"Unsupported provider: {name}"
            )

        provider_class = cls._provider_classes.get(name)

        if provider_class is None:
            raise ValueError(
                f"No implementation registered for provider: {name}"
            )

        return provider_class()