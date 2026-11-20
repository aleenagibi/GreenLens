"""Convert EcoLogits impacts into GreenLens units."""
from typing import Any
from ecologits.utils.range_value import RangeValue


class EcoLogitsAdapter:
    """EcoLogits reports energy in kWh, GWP in kgCO2eq and WCF in L."""

    @staticmethod
    def _numeric_value(value: int | float | RangeValue) -> float:
        # GreenLens currently stores a representative midpoint for ranges.
        if isinstance(value, RangeValue):
            return (float(value.min) + float(value.max)) / 2.0
        if hasattr(value, "min") and hasattr(value, "max"):
            return (float(value.min) + float(value.max)) / 2.0
        return float(value)

    @classmethod
    def extract(cls, impacts: Any) -> dict[str, float | None] | None:
        if impacts is None:
            return None

        energy = getattr(impacts, "energy", None)
        gwp = getattr(impacts, "gwp", None)
        wcf = getattr(impacts, "wcf", None)

        if energy is None or gwp is None:
            return None
        if not hasattr(energy, "value") or not hasattr(gwp, "value"):
            return None

        energy_kwh = cls._numeric_value(energy.value)
        gwp_kg = cls._numeric_value(gwp.value)
        water_l = None
        if wcf is not None and getattr(wcf, "value", None) is not None:
            try:
                water_l = cls._numeric_value(wcf.value)
            except (TypeError, ValueError, AttributeError):
                water_l = None

        return {
            "energy_wh": round(energy_kwh * 1000.0, 6),
            "carbon_g": round(gwp_kg * 1000.0, 8),
            "water_l": round(water_l, 9) if water_l is not None else None,
        }
