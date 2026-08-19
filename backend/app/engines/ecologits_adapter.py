"""
EcoLogits Adapter

Converts EcoLogits environmental impact results
into the format used by GreenLens.
"""

from typing import Any

from ecologits.impacts.modeling import Energy, GWP
from ecologits.utils.range_value import RangeValue


class EcoLogitsAdapter:
    """
    Adapter between EcoLogits and GreenLens.

    EcoLogits reports:
        Energy -> kWh
        GWP    -> kgCO2eq

    GreenLens stores:
        Energy -> Wh
        Carbon -> gCO2eq
    """

    @staticmethod
    def _numeric_value(
        value: int | float | RangeValue,
    ) -> float:
        """
        Convert a numeric or RangeValue into one
        representative numeric value.

        For a range, the midpoint is used.
        """

        if isinstance(value, RangeValue):
            return (
                float(value.min)
                + float(value.max)
            ) / 2

        return float(value)

    @classmethod
    def extract(
        cls,
        impacts: Any,
    ) -> dict[str, float] | None:
        """
        Extract energy and carbon information
        from an EcoLogits impacts object.

        Returns None when EcoLogits does not provide
        both required environmental metrics.
        """

        if impacts is None:
            return None

        energy = getattr(
            impacts,
            "energy",
            None,
        )

        gwp = getattr(
            impacts,
            "gwp",
            None,
        )

        if energy is None or gwp is None:
            return None

        if not hasattr(energy, "value"):
            return None

        if not hasattr(gwp, "value"):
            return None

        energy_kwh = cls._numeric_value(
            energy.value
        )

        gwp_kg = cls._numeric_value(
            gwp.value
        )

        return {
            "energy_wh": round(
                energy_kwh * 1000,
                4,
            ),
            "carbon_g": round(
                gwp_kg * 1000,
                4,
            ),
        }