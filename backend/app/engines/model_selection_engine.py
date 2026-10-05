"""
Model Selection Engine

Selects:
1. The ideal model based on the GreenLens
   optimization score.
2. The closest suitable free alternative
   when the ideal model is paid.
3. Uses verified capability when available
   without inventing unavailable evidence.
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
        verified capability to the ideal model.
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
        Capability-based model selection.

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
        if not candidates:
            raise ValueError("No model candidates available.")

        # --------------------------------------------------
        # 1. Ideal model = highest GreenLens optimization score
        # --------------------------------------------------

        ideal = max(
            candidates,
            key=lambda candidate: candidate["score"],
        )

        # --------------------------------------------------
        # 2. Select the actual free model
        # --------------------------------------------------

        if ideal.get("is_free", False):
            selected = ideal

        else:
            free_candidates = [
                candidate
                for candidate in candidates
                if candidate.get("is_free", False)
            ]

            if not free_candidates:
                raise ValueError(
                    "Ideal model is paid and no free model is available."
                )

            ideal_capability = ideal.get("capability_score")

            capable_free_candidates = [
                candidate
                for candidate in free_candidates
                if candidate.get("capability_score") is not None
            ]

            # --------------------------------------------------
            # Capability-aware paid -> free substitution
            # --------------------------------------------------

            if (
                ideal_capability is not None
                and capable_free_candidates
            ):
                suitable = [
                    candidate
                    for candidate in capable_free_candidates
                    if candidate["capability_score"] <= ideal_capability
                ]

                if suitable:
                    selected = max(
                        suitable,
                        key=lambda candidate: candidate["capability_score"],
                    )
                else:
                    selected = min(
                        capable_free_candidates,
                        key=lambda candidate: abs(
                            candidate["capability_score"]
                            - ideal_capability
                        ),
                    )

                selection_basis = "capability_verified"

            # --------------------------------------------------
            # Capability unavailable -> do NOT pretend we know
            # the capability gap.
            # --------------------------------------------------

            else:
                selected = max(
                    free_candidates,
                    key=lambda candidate: candidate["score"],
                )

                selection_basis = "greenlens_score_fallback"

        # --------------------------------------------------
        # 3. Capability gap
        # --------------------------------------------------

        ideal_capability = ideal.get("capability_score")
        selected_capability = selected.get("capability_score")

        if (
            ideal_capability is not None
            and selected_capability is not None
        ):
            capability_gap = round(
                ideal_capability - selected_capability,
                2,
            )
        else:
            capability_gap = None

        # --------------------------------------------------
        # 4. Explain the actual selection basis
        # --------------------------------------------------

        if ideal["model"] == selected["model"]:

            reason = (
                f"{selected['model']} was selected because it achieved "
                f"the highest GreenLens optimization score of "
                f"{selected['score']:.2f}/10."
            )

        elif selection_basis == "capability_verified":

            reason = (
                f"{ideal['model']} achieved the highest GreenLens "
                f"optimization score of {ideal['score']:.2f}/10 but "
                f"is paid. {selected['model']} was selected as the "
                f"closest suitable free alternative based on verified "
                f"capability."
            )

        else:

            reason = (
                f"{ideal['model']} achieved the highest GreenLens "
                f"optimization score of {ideal['score']:.2f}/10 but "
                f"is paid. Verified capability data was unavailable "
                f"for the required comparison, so GreenLens selected "
                f"{selected['model']} as the highest-scoring free "
                f"alternative."
            )

        return {
            "ideal_model": ideal["model"],
            "selected_model": selected["model"],
            "ideal_is_free": ideal.get("is_free", False),
            "selected_is_free": selected.get("is_free", False),

            # None means "not measurable", NOT zero gap.
            "capability_gap": capability_gap,

            "capability_available": (
                ideal_capability is not None
                and selected_capability is not None
            ),

            "selection_basis": selection_basis,

            "score": selected["score"],
            "reason": reason,
        }