from app.engines.complexity_engine import ComplexityEngine


def test_simple_prompt():
    result = ComplexityEngine.estimate(
        "What is artificial intelligence?"
    )

    assert result.level == "low"
    assert 0 <= result.score <= 10


def test_complex_prompt():
    result = ComplexityEngine.estimate(
        "Design and implement a Python algorithm "
        "to analyze and optimize a large dataset."
    )

    assert result.level in {"medium", "high"}
    assert result.score > 3
    assert len(result.factors) > 0