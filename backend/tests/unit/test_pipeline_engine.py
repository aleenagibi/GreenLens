from app.engines.capability_engine import CapabilityEngine
from app.engines.pipeline_engine import PipelineEngine


def test_pipeline():

    CapabilityEngine._profiles = {
        "openai/gpt-oss-20b:free": {
            "model": "openai/gpt-oss-20b:free",
            "coding": 90.0,
            "overall": 90.0,
        }
    }

    pipeline = PipelineEngine()

    models = [
        {
            "model": "openai/gpt-oss-20b:free",
            "estimated_tokens": 500,
            "latency_score": 8.0,
        }
    ]

    result = pipeline.run(
        prompt="Write a Python program to sort a list.",
        models=models,
    )

    assert "task" in result
    assert "selection" in result
    assert "explanation" in result

    assert (
        result["selection"]["selected_model"]
        == "openai/gpt-oss-20b:free"
    )

    assert (
        result["task"]["embedding_dimensions"]
        == 384
    )