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

    PRESET_WEIGHTS = {
        "balanced": {
            "capability": 0.40,
            "carbon": 0.30,
            "latency": 0.20,
            "complexity": 0.10,
        },
        "quality": {
            "capability": 0.60,
            "carbon": 0.20,
            "latency": 0.10,
            "complexity": 0.10,
        },
        "eco": {
            "capability": 0.25,
            "carbon": 0.55,
            "latency": 0.10,
            "complexity": 0.10,
        },
    }

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
        preset: str = "balanced",
    ) -> OptimizationResult:
        """
        Calculate the overall model score.

        If capability_score is None, no artificial
        capability value is introduced.

        The remaining objective weights are
        renormalized so that the final score remains
        on a 0–10 scale.
        """

        preset = preset.lower()
        if preset not in cls.PRESET_WEIGHTS:
            raise ValueError(
                f"Unknown optimization preset: {preset}. "
                f"Expected one of: {', '.join(cls.PRESET_WEIGHTS)}"
            )

        weights = cls.PRESET_WEIGHTS[preset]
        components = []

        if capability_score is not None:

            components.append(
                (
                    capability_score,
                    weights["capability"],
                )
            )

        components.extend(
            [
                (
                    carbon_score,
                    weights["carbon"],
                ),
                (
                    latency_score,
                    weights["latency"],
                ),
                (
                    complexity_score,
                    weights["complexity"],
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