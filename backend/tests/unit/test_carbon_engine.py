from app.engines.carbon_engine import CarbonEngine


def test_carbon_estimation():
    result = CarbonEngine.estimate(582)

    assert result.energy_wh == 0.291
    assert result.carbon_g == 0.1286
    assert result.green_score == 7.75


def test_zero_tokens():
    result = CarbonEngine.estimate(0)

    assert result.energy_wh == 0.0
    assert result.carbon_g == 0.0
    assert result.green_score == 10.0