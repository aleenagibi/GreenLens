from types import SimpleNamespace

from app.engines.sustainability_engine import (
    SustainabilityEngine,
)


def test_sustainability_uses_carbon_fallback():
    result = SustainabilityEngine.calculate(
        total_tokens=582,
        eco_impacts=None,
    )

    assert result.energy_wh == 0.291
    assert result.carbon_g == 0.1286
    assert result.green_score == 7.75


def test_sustainability_uses_ecologits():

    impacts = SimpleNamespace(
        energy=SimpleNamespace(
            value=0.002,
            unit="kWh",
        ),
        gwp=SimpleNamespace(
            value=0.001,
            unit="kgCO2eq",
        ),
    )

    result = SustainabilityEngine.calculate(
        total_tokens=582,
        eco_impacts=impacts,
    )

    assert result.energy_wh == 2.0
    assert result.carbon_g == 1.0


def test_sustainability_uses_range_values():

    from ecologits.utils.range_value import (
        RangeValue,
    )

    impacts = SimpleNamespace(
        energy=SimpleNamespace(
            value=RangeValue(
                min=0.002,
                max=0.004,
            ),
            unit="kWh",
        ),
        gwp=SimpleNamespace(
            value=RangeValue(
                min=0.001,
                max=0.003,
            ),
            unit="kgCO2eq",
        ),
    )

    result = SustainabilityEngine.calculate(
        total_tokens=582,
        eco_impacts=impacts,
    )

    assert result.energy_wh == 3.0
    assert result.carbon_g == 2.0


def test_sustainability_missing_energy_uses_fallback():

    impacts = SimpleNamespace(
        energy=None,
        gwp=SimpleNamespace(
            value=0.001,
        ),
    )

    result = SustainabilityEngine.calculate(
        total_tokens=582,
        eco_impacts=impacts,
    )

    assert result.energy_wh == 0.291
    assert result.carbon_g == 0.1286
    assert result.green_score == 7.75