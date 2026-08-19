from types import SimpleNamespace

from app.engines.ecologits_adapter import (
    EcoLogitsAdapter,
)
from ecologits.utils.range_value import RangeValue


def test_numeric_values():

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

    result = EcoLogitsAdapter.extract(
        impacts
    )

    assert result is not None

    assert result["energy_wh"] == 2.0
    assert result["carbon_g"] == 1.0


def test_range_values():

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

    result = EcoLogitsAdapter.extract(
        impacts
    )

    assert result is not None

    # Energy midpoint:
    # (0.002 + 0.004) / 2 = 0.003 kWh
    # 0.003 kWh = 3 Wh
    assert result["energy_wh"] == 3.0

    # GWP midpoint:
    # (0.001 + 0.003) / 2 = 0.002 kg
    # 0.002 kg = 2 g
    assert result["carbon_g"] == 2.0


def test_missing_impacts():

    result = EcoLogitsAdapter.extract(
        None
    )

    assert result is None


def test_missing_energy():

    impacts = SimpleNamespace(
        energy=None,
        gwp=SimpleNamespace(
            value=0.001,
        ),
    )

    result = EcoLogitsAdapter.extract(
        impacts
    )

    assert result is None


def test_missing_gwp():

    impacts = SimpleNamespace(
        energy=SimpleNamespace(
            value=0.002,
        ),
        gwp=None,
    )

    result = EcoLogitsAdapter.extract(
        impacts
    )

    assert result is None
    