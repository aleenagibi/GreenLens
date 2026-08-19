"""
Constraint Optimizer

Combines model capability, task complexity,
carbon impact, and performance into one score.
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
    """

    CAPABILITY_WEIGHT = 0.40
    CARBON_WEIGHT = 0.30
    LATENCY_WEIGHT = 0.20
    COMPLEXITY_WEIGHT = 0.10

    @classmethod
    def optimize(
        cls,
        model: str,
        capability_score: float,
        carbon_score: float,
        latency_score: float,
        complexity_score: float,
    ) -> OptimizationResult:
        """
        Calculate the overall model score.
        """

        score = (
            capability_score * cls.CAPABILITY_WEIGHT
            + carbon_score * cls.CARBON_WEIGHT
            + latency_score * cls.LATENCY_WEIGHT
            + complexity_score * cls.COMPLEXITY_WEIGHT
        )

        score = round(
            max(0.0, min(10.0, score)),
            2,
        )

        reason = (
            "Selected based on a balance of "
            "task capability, carbon impact, "
            "latency, and task complexity."
        )

        return OptimizationResult(
            model=model,
            score=score,
            reason=reason,
        )