"""
Model Registry

Central registry for individual AI models.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInfo:
    model_id: str
    provider: str
    display_name: str
    is_free: bool
    capability_score: float | None = None


class ModelRegistry:

    _models: dict[str, ModelInfo] = {}

    @classmethod
    def load_models(
        cls,
        models: list[dict],
    ) -> None:
        """
        Load normalized model metadata into the registry.
        """

        cls._models.clear()

        for model in models:

            model_id = model.get("model_id")

            if not model_id:
                continue

            # OpenRouter model IDs normally look like:
            # provider/model-name
            provider = model_id.split("/", 1)[0]

            cls._models[model_id] = ModelInfo(
                model_id=model_id,
                provider=provider,
                display_name=model.get(
                    "display_name",
                    model_id,
                ),
                is_free=model.get(
                    "is_free",
                    False,
                ),
                capability_score=None,
            )

    @classmethod
    def get_all(cls) -> list[ModelInfo]:
        return list(cls._models.values())

    @classmethod
    def get_free_models(cls) -> list[ModelInfo]:
        return [
            model
            for model in cls._models.values()
            if model.is_free
        ]

    @classmethod
    def get_paid_models(cls) -> list[ModelInfo]:
        return [
            model
            for model in cls._models.values()
            if not model.is_free
        ]

    @classmethod
    def get_by_id(
        cls,
        model_id: str,
    ) -> ModelInfo | None:

        return cls._models.get(model_id)