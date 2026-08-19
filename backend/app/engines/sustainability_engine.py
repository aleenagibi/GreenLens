"""
Sustainability Engine

Estimates energy consumption and carbon emissions
for AI inference requests using EcoLogits when
available, with a GreenLens fallback otherwise.
"""

from dataclasses import dataclass
from typing import Any

from app.engines.carbon_engine import CarbonEngine
from app.engines.ecologits_adapter import (
    EcoLogitsAdapter,
)


@dataclass
class SustainabilityResult:
    """
    Sustainability metrics for a single inference request.
    """

    energy_wh: float
    carbon_g: float
    green_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "energy_wh": self.energy_wh,
            "carbon_g": self.carbon_g,
            "green_score": self.green_score,
        }


class SustainabilityEngine:
    """
    Estimates environmental impact of AI inference.

    EcoLogits is used when valid environmental impact
    data is available. Otherwise, CarbonEngine provides
    the fallback estimate.
    """

    @classmethod
    def calculate(
        cls,
        total_tokens: int,
        eco_impacts: Any = None,
    ) -> SustainabilityResult:
        """
        Calculate environmental impact.

        Uses EcoLogits when valid energy and GWP
        information is available. Otherwise falls
        back to CarbonEngine.
        """

        ecologits_result = (
            EcoLogitsAdapter.extract(
                eco_impacts
            )
        )

        if ecologits_result is not None:

            energy_wh = ecologits_result[
                "energy_wh"
            ]

            carbon_g = ecologits_result[
                "carbon_g"
            ]

            green_score = cls._calculate_green_score(
                energy_wh
            )

            return SustainabilityResult(
                energy_wh=round(
                    energy_wh,
                    4,
                ),
                carbon_g=round(
                    carbon_g,
                    4,
                ),
                green_score=round(
                    green_score,
                    2,
                ),
            )

        fallback = CarbonEngine.estimate(
            total_tokens=total_tokens
        )

        return SustainabilityResult(
            energy_wh=fallback.energy_wh,
            carbon_g=fallback.carbon_g,
            green_score=fallback.green_score,
        )

    @staticmethod
    def _calculate_green_score(
        energy_wh: float,
    ) -> float:
        """
        Calculate a normalized sustainability score
        from 0–10.

        Lower energy consumption produces a
        higher score.
        """

        if energy_wh <= 0:
            return 10.0

        score = 10 / (1 + energy_wh)

        return max(
            0.0,
            min(10.0, score),
        )