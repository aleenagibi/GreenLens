"""
Constraint Optimizer

Combines model capability, carbon impact,
latency, and task complexity into one score.

If verified capability data is unavailable,
the optimizer does not invent a capability score.
Instead, it renormalizes the weights of the
available objectives.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OptimizationResult:
    model: str
    score: float
    reason: str

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "score": self.score,
            "reason": self.reason,
        }


class OptimizerEngine:
    """
    Level 1 weighted multi-objective optimizer.

    Capability has the highest weight when verified
    benchmark evidence is available.

    If capability is unavailable, its weight is
    redistributed proportionally across the remaining
    available objectives.
    """

    CAPABILITY_WEIGHT = 0.40
    CARBON_WEIGHT = 0.30
    LATENCY_WEIGHT = 0.20
    COMPLEXITY_WEIGHT = 0.10

    @classmethod
    def optimize(
        cls,
        model: str,
        capability_score: float | None,
        carbon_score: float,
        latency_score: float,
        complexity_score: float,
    ) -> OptimizationResult:
        """
        Calculate the overall model score.

        If capability_score is None, no artificial
        capability value is introduced.

        The remaining objective weights are
        renormalized so that the final score remains
        on a 0–10 scale.
        """

        components = []

        if capability_score is not None:

            components.append(
                (
                    capability_score,
                    cls.CAPABILITY_WEIGHT,
                )
            )

        components.extend(
            [
                (
                    carbon_score,
                    cls.CARBON_WEIGHT,
                ),
                (
                    latency_score,
                    cls.LATENCY_WEIGHT,
                ),
                (
                    complexity_score,
                    cls.COMPLEXITY_WEIGHT,
                ),
            ]
        )

        total_weight = sum(
            weight
            for _, weight in components
        )

        weighted_score = sum(
            value * weight
            for value, weight in components
        )

        score = weighted_score / total_weight

        score = round(
            max(
                0.0,
                min(
                    10.0,
                    score,
                ),
            ),
            2,
        )

        if capability_score is None:

            reason = (
                "Capability benchmark data was "
                "unavailable, so the score was "
                "calculated using the available "
                "carbon, latency, and task complexity "
                "objectives."
            )

        else:

            reason = (
                "Selected based on a balance of "
                "verified task capability, carbon "
                "impact, latency, and task complexity."
            )

        return OptimizationResult(
            model=model,
            score=score,
            reason=reason,
        )