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

        ranked = sorted(
            candidates,
            key=lambda candidate: candidate["score"],
            reverse=True,
        )

        comparison = []

        for rank, candidate in enumerate(ranked, start=1):
            comparison.append(
                {
                    "rank": rank,
                    "model": candidate["model"],
                    "display_name": candidate.get("display_name"),
                    "provider": candidate.get("provider"),
                    "is_free": candidate.get("is_free", False),
                    "fit_score": candidate["score"],
                    "capability_score": candidate.get("capability_score"),
                    "capability_source": candidate.get(
                        "capability_source", "unavailable"
                    ),
                    "carbon_score": candidate.get("carbon_score"),
                    "latency_score": candidate.get("latency_score"),
                    "complexity_score": candidate.get("complexity_score"),
                    "estimated_energy_wh": candidate.get("energy_wh"),
                    "estimated_carbon_g": candidate.get("carbon_g"),
                    "selected": candidate["model"] == selected_model,
                    "ideal": candidate["model"] == ranked[0]["model"],
                }
            )

        ideal = ranked[0]

        if ideal["model"] == selected_model:
            summary = (
                f"{selected.get('display_name') or selected_model} was selected "
                f"as the best available fit for this task. GreenLens considered "
                f"capability, estimated environmental impact, latency, and task "
                f"complexity. The model is available for free execution."
            )
        else:
            summary = (
                f"{ideal.get('display_name') or ideal['model']} ranked highest as "
                f"the ideal model for this task, but it is not free. GreenLens "
                f"therefore selected {selected.get('display_name') or selected_model}, "
                f"the closest suitable free alternative based on verified capability."
            )

        return ExplanationResult(
            selected_model=selected_model,
            summary=summary,
            comparison=comparison,
        )