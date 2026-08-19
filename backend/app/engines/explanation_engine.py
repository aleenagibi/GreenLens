"""
Explanation Engine

Creates a transparent explanation for the model selection.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExplanationResult:
    selected_model: str
    summary: str
    comparison: list[dict]

    def to_dict(self) -> dict:
        return {
            "selected_model": self.selected_model,
            "summary": self.summary,
            "comparison": self.comparison,
        }


class ExplanationEngine:
    """
    Generates a simple, explainable model-selection summary.
    """

    @staticmethod
    def explain(
        selected_model: str,
        candidates: list[dict],
    ) -> ExplanationResult:

        if not candidates:
            raise ValueError(
                "No candidate models available."
            )

        selected = next(
            (
                candidate
                for candidate in candidates
                if candidate["model"] == selected_model
            ),
            None,
        )

        if selected is None:
            raise ValueError(
                "Selected model is not present in candidates."
            )

        comparison = []

        for candidate in candidates:
            comparison.append(
                {
                    "model": candidate["model"],
                    "score": candidate["score"],
                    "capability_score": candidate.get(
                        "capability_score", 0.0
                    ),
                    "carbon_score": candidate.get(
                        "carbon_score", 0.0
                    ),
                    "latency_score": candidate.get(
                        "latency_score", 0.0
                    ),
                    "complexity_score": candidate.get(
                        "complexity_score", 0.0
                    ),
                }
            )

        summary = (
            f"{selected_model} was selected because it achieved "
            f"the highest overall score of "
            f"{selected['score']}/10 after considering "
            f"capability, carbon impact, latency, and "
            f"task complexity."
        )

        return ExplanationResult(
            selected_model=selected_model,
            summary=summary,
            comparison=comparison,
        )