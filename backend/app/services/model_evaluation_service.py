"""
Model Evaluation Service

Combines the model catalogue with capability evidence
for a specific task.
"""

from app.engines.capability_engine import CapabilityEngine
from app.models.model_registry import ModelRegistry


class ModelEvaluationService:

    @classmethod
    def evaluate_models(
        cls,
        task_type: str,
        free_only: bool = False,
    ) -> list[dict]:
        """
        Evaluate available models for a specific task.

        Capability source priority:

        1. LiveBench
        2. Artificial Analysis
        3. Unavailable
        """

        models = (
            ModelRegistry.get_free_models()
            if free_only
            else ModelRegistry.get_all()
        )

        results = []

        for model in models:

            capability = CapabilityEngine.predict(
                model=model.model_id,
                task_type=task_type,
                model_metadata={
                    "artificial_analysis": (
                        model.artificial_analysis
                    ),
                },
            )

            results.append(
                {
                    "model": model.model_id,
                    "display_name": model.display_name,
                    "provider": model.provider,
                    "is_free": model.is_free,
                    "capability_score": capability.score,
                    "capability_source": capability.source,
                    "capability_available": (
                        capability.available
                    ),
                }
            )

        return results

    @classmethod
    def get_capable_models(
        cls,
        task_type: str,
        free_only: bool = False,
    ) -> list[dict]:
        """
        Return only models for which verified
        capability data is available.
        """

        results = cls.evaluate_models(
            task_type=task_type,
            free_only=free_only,
        )

        return [
            result
            for result in results
            if result["capability_available"]
        ]