"""
Model Selection Engine

Selects:
1. The ideal model based on capability.
2. The best free alternative based on capability.
3. Supports the existing Level-1 candidate-based pipeline.
"""

from app.services.model_evaluation_service import (
    ModelEvaluationService,
)


class ModelSelectionEngine:

    @classmethod
    def select_ideal_model(
        cls,
        task_type: str,
    ) -> dict:
        """
        Select the model with the highest verified
        capability for the given task.
        """

        candidates = (
            ModelEvaluationService.get_capable_models(
                task_type=task_type,
                free_only=False,
            )
        )

        if not candidates:
            raise ValueError(
                f"No capability data available "
                f"for task: {task_type}"
            )

        return max(
            candidates,
            key=lambda model: model[
                "capability_score"
            ],
        )

    @classmethod
    def select_best_free_model(
        cls,
        task_type: str,
        ideal_score: float,
    ) -> dict:
        """
        Select the free model with the closest
        capability to the ideal model.
        """

        candidates = (
            ModelEvaluationService.get_capable_models(
                task_type=task_type,
                free_only=True,
            )
        )

        if not candidates:
            raise ValueError(
                "No free model with verified "
                "capability data is available."
            )

        suitable = [
            model
            for model in candidates
            if model["capability_score"]
            <= ideal_score
        ]

        if suitable:
            return max(
                suitable,
                key=lambda model: model[
                    "capability_score"
                ],
            )

        return min(
            candidates,
            key=lambda model: abs(
                model["capability_score"]
                - ideal_score
            ),
        )

    @classmethod
    def select(
        cls,
        task_type: str,
    ) -> dict:
        """
        New model-selection flow.

        Finds the ideal model and, if necessary,
        the closest capable free alternative.
        """

        ideal = cls.select_ideal_model(
            task_type
        )

        if ideal["is_free"]:
            selected = ideal

        else:
            selected = cls.select_best_free_model(
                task_type=task_type,
                ideal_score=ideal[
                    "capability_score"
                ],
            )

        return {
            "ideal_model": ideal,
            "selected_model": selected,
            "capability_gap": round(
                ideal["capability_score"]
                - selected["capability_score"],
                2,
            ),
        }

    @classmethod
    def select_from_candidates(
        cls,
        candidates: list[dict],
    ) -> dict:
        """
        Compatibility method for the existing
        Level-1 PipelineEngine.

        Selects the highest-scoring candidate.
        """

        if not candidates:
            raise ValueError(
                "No model candidates available."
            )

        selected = max(
            candidates,
            key=lambda candidate: candidate[
                "score"
            ],
        )

        return {
            "ideal_model": selected["model"],
            "selected_model": selected["model"],
            "capability_gap": 0.0,
            "score": selected["score"],
            "reason": (
                f"{selected['model']} was selected "
                f"because it achieved the highest "
                f"overall score of "
                f"{selected['score']:.2f}/10."
            ),
        }