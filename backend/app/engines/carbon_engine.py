"""
Carbon Engine

Estimates energy consumption and carbon emissions
for an AI inference request.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CarbonResult:
    energy_wh: float
    carbon_g: float
    green_score: float

    def to_dict(self) -> dict:
        return {
            "energy_wh": self.energy_wh,
            "carbon_g": self.carbon_g,
            "green_score": self.green_score,
        }


class CarbonEngine:
    """
    Level 1 carbon estimation.

    This is a simplified prototype and will later
    be replaced/enhanced using EcoLogits.
    """

    ENERGY_PER_1000_TOKENS_WH = 0.5
    CARBON_INTENSITY_G_PER_KWH = 442.0

    @classmethod
    def estimate(
        cls,
        total_tokens: int,
    ) -> CarbonResult:
        """
        Estimate energy and carbon emissions.
        """

        energy_wh = (
            total_tokens / 1000
        ) * cls.ENERGY_PER_1000_TOKENS_WH

        energy_kwh = energy_wh / 1000

        carbon_g = (
            energy_kwh
            * cls.CARBON_INTENSITY_G_PER_KWH
        )

        green_score = (
            10 / (1 + energy_wh)
        )

        return CarbonResult(
            energy_wh=round(energy_wh, 4),
            carbon_g=round(carbon_g, 4),
            green_score=round(
                max(0.0, min(10.0, green_score)),
                2,
            ),
        )