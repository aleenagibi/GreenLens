"""
OpenRouter Model Catalog Service

Fetches the current model catalogue from OpenRouter.
This service is responsible only for retrieving and
normalizing model metadata.
"""

from typing import Any

import requests

from app.core.config import settings


class ModelCatalogService:

    OPENROUTER_MODELS_URL = (
        "https://openrouter.ai/api/v1/models"
    )

    @classmethod
    def fetch_models(cls) -> list[dict[str, Any]]:
        """
        Fetch all models currently listed by OpenRouter.
        """

        response = requests.get(
            cls.OPENROUTER_MODELS_URL,
            timeout=15,
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
        Convert OpenRouter metadata into the fields
        GreenLens needs.
        """

        pricing = model.get("pricing", {})

        prompt_price = float(
            pricing.get("prompt", 0)
        )

        completion_price = float(
            pricing.get("completion", 0)
        )

        return {
            "model_id": model.get("id"),
            "display_name": model.get("name"),
            "context_length": model.get(
                "context_length"
            ),
            "is_free": (
                prompt_price == 0
                and completion_price == 0
            ),
            "prompt_price": prompt_price,
            "completion_price": completion_price,
            "input_modalities": model.get(
                "architecture", {}
            ).get("input_modalities", []),
            "output_modalities": model.get(
                "architecture", {}
            ).get("output_modalities", []),
            "supports_reasoning": (
                "reasoning" in model
            ),
            "artificial_analysis": model.get(
                "benchmarks", {}
            ).get(
                "artificial_analysis"
            ),
        }

    @classmethod
    def get_normalized_models(
        cls,
    ) -> list[dict[str, Any]]:
        """
        Fetch and normalize the complete catalogue.
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
        Return currently free models.
        """

        models = cls.get_normalized_models()

        return [
            model
            for model in models
            if model["is_free"]
        ]