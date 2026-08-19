from app.engines.explanation_engine import (
    ExplanationEngine,
)


def test_explanation():

    candidates = [
        {
            "model": "model-a",
            "score": 7.8,
            "capability_score": 8.0,
            "carbon_score": 7.5,
            "latency_score": 8.0,
            "complexity_score": 7.0,
        },
        {
            "model": "model-b",
            "score": 8.9,
            "capability_score": 9.0,
            "carbon_score": 8.5,
            "latency_score": 9.0,
            "complexity_score": 8.0,
        },
    ]

    result = ExplanationEngine.explain(
        selected_model="model-b",
        candidates=candidates,
    )

    assert result.selected_model == "model-b"
    assert "highest overall score" in result.summary
    assert len(result.comparison) == 2