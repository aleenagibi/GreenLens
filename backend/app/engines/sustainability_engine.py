"""Estimate per-inference environmental impact."""
from dataclasses import dataclass
from typing import Any

from app.engines.carbon_engine import CarbonEngine
from app.engines.ecologits_adapter import EcoLogitsAdapter


@dataclass
class SustainabilityResult:
    energy_wh: float
    carbon_g: float
    green_score: float
    water_l: float | None = None
    source: str = "carbon_engine_fallback"

    def to_dict(self) -> dict[str, Any]:
        return {
            "energy_wh": self.energy_wh,
            "carbon_g": self.carbon_g,
            "green_score": self.green_score,
            "water_l": self.water_l,
            "source": self.source,
        }


class SustainabilityEngine:
    """Use EcoLogits impacts when available; otherwise use GreenLens fallback."""

    @classmethod
    def calculate(cls, total_tokens: int, eco_impacts: Any = None) -> SustainabilityResult:
        result = EcoLogitsAdapter.extract(eco_impacts)
        if result is not None:
            energy_wh = float(result["energy_wh"])
            return SustainabilityResult(
                energy_wh=energy_wh,
                carbon_g=float(result["carbon_g"]),
                green_score=round(cls._calculate_green_score(energy_wh), 2),
                water_l=result.get("water_l"),
                source="ecologits",
            )

        fallback = CarbonEngine.estimate(total_tokens=total_tokens)
        return SustainabilityResult(
            energy_wh=fallback.energy_wh,
            carbon_g=fallback.carbon_g,
            green_score=fallback.green_score,
            water_l=None,
            source="greenlens_token_fallback",
        )

    @staticmethod
    def _calculate_green_score(energy_wh: float) -> float:
        if energy_wh <= 0:
            return 10.0
        return max(0.0, min(10.0, 10.0 / (1.0 + energy_wh)))
