"""
OpenRouter Model Catalog Service

Fetches the current model catalogue from OpenRouter
and normalizes the metadata required by GreenLens.

This service is responsible only for:
    1. Fetching model metadata.
    2. Normalizing model metadata.
    3. Filtering free/paid models.
    4. Filtering models suitable for text chat.

Model selection and capability evaluation are handled
by separate services/engines.
"""

from typing import Any

import requests


class ModelCatalogService:
    """
    Service responsible for retrieving the current
    OpenRouter model catalogue.
    """

    OPENROUTER_MODELS_URL = (
        "https://openrouter.ai/api/v1/models"
    )

    REQUEST_TIMEOUT = 15

    @classmethod
    def fetch_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Fetch all models currently listed by OpenRouter.
        """

        response = requests.get(
            cls.OPENROUTER_MODELS_URL,
            timeout=cls.REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("data", [])

    @classmethod
    def normalize_model(
        cls,
        model: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert OpenRouter metadata into the normalized
        structure used by GreenLens.
        """

        pricing = model.get("pricing") or {}
        architecture = model.get("architecture") or {}

        prompt_price = cls._parse_price(
            pricing.get("prompt")
        )

        completion_price = cls._parse_price(
            pricing.get("completion")
        )

        model_id = model.get("id")

        provider = None

        if model_id and "/" in model_id:
            provider = model_id.split(
                "/",
                1,
            )[0]

        return {
            # Identity
            "model_id": model_id,
            "display_name": model.get("name"),
            "provider": provider,

            # Context
            "context_length": model.get(
                "context_length"
            ),

            # Pricing
            "prompt_price": prompt_price,
            "completion_price": completion_price,
            "is_free": (
                prompt_price == 0.0
                and completion_price == 0.0
            ),

            # Modalities
            "input_modalities": architecture.get(
                "input_modalities",
                [],
            ),
            "output_modalities": architecture.get(
                "output_modalities",
                [],
            ),

            # Capabilities
            "supports_reasoning": (
                "reasoning"
                in model
                or "reasoning"
                in model.get(
                    "supported_parameters",
                    [],
                )
            ),

            "supported_parameters": model.get(
                "supported_parameters",
                [],
            ),

            # Benchmark information exposed by
            # OpenRouter, if available.
            "artificial_analysis": (
                model.get(
                    "benchmarks",
                    {},
                ) or {}
            ).get(
                "artificial_analysis"
            ),
        }

    @classmethod
    def get_normalized_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Fetch and normalize the complete OpenRouter
        model catalogue.
        """

        models = cls.fetch_models()

        return [
            cls.normalize_model(model)
            for model in models
        ]

    @classmethod
    def get_free_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return all currently free models.
        """

        models = cls.get_normalized_models()

        return [
            model
            for model in models
            if model["is_free"]
        ]

    @classmethod
    def get_paid_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return all currently paid models.
        """

        models = cls.get_normalized_models()

        return [
            model
            for model in models
            if not model["is_free"]
        ]

    @classmethod
    def get_text_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return models capable of accepting text input
        and producing text output.
        """

        models = cls.get_normalized_models()

        return [
            model
            for model in models
            if (
                "text" in model["input_modalities"]
                and "text" in model["output_modalities"]
            )
        ]

    @classmethod
    def get_chat_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return models suitable for GreenLens text chat.

        A chat candidate must:
        - have a valid model ID
        - accept text input
        - produce text output
        - not be the OpenRouter automatic router
        """

        models = cls.get_text_models()

        return [
            model
            for model in models
            if (
                model["model_id"]
                and model["model_id"]
                != "openrouter/free"
            )
        ]

    @classmethod
    def get_free_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return all currently free models.
        """

        models = cls.get_normalized_models()

        return [
            model
            for model in models
            if model["is_free"]
        ]

    @classmethod
    def get_paid_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return all currently paid models.
        """

        models = cls.get_normalized_models()

        return [
            model
            for model in models
            if not model["is_free"]
        ]

    @classmethod
    def get_free_text_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return free models suitable for text-based
        GreenLens inference.
        """

        models = cls.get_text_models()

        return [
            model
            for model in models
            if model["is_free"]
        ]

    @classmethod
    def get_paid_text_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return paid models suitable for text-based
        GreenLens inference.
        """

        models = cls.get_text_models()

        return [
            model
            for model in models
            if not model["is_free"]
        ]

    @classmethod
    def get_free_chat_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return free models suitable for GreenLens
        text-based chat inference.
        """

        models = cls.get_chat_models()

        return [
            model
            for model in models
            if model["is_free"]
        ]

    @classmethod
    def get_paid_chat_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Return paid models suitable for GreenLens
        text-based chat inference.
        """

        models = cls.get_chat_models()

        return [
            model
            for model in models
            if not model["is_free"]
        ]

    @staticmethod
    def _parse_price(
        value: Any,
    ) -> float:
        """
        Safely convert OpenRouter pricing values
        into floats.

        OpenRouter pricing is returned as strings.
        Missing or invalid values are treated as zero.
        """

        if value is None:
            return 0.0

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0