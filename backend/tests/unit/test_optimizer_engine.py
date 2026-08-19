from app.engines.optimizer_engine import OptimizerEngine


def test_optimizer():
    result = OptimizerEngine.optimize(
        model="openai/gpt-oss-20b:free",
        capability_score=9.0,
        carbon_score=8.0,
        latency_score=8.0,
        complexity_score=7.0,
    )

    assert result.model == "openai/gpt-oss-20b:free"
    assert result.score == 8.3
    assert result.score <= 10.0
    assert result.score >= 0.0
    assert result.reason


def test_score_bounds():
    result = OptimizerEngine.optimize(
        model="test-model",
        capability_score=10.0,
        carbon_score=10.0,
        latency_score=10.0,
        complexity_score=10.0,
    )

    assert result.score == 10.0