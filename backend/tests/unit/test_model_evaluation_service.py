import json

from app.engines.capability_engine import (
    CapabilityEngine,
)
from app.models.model_registry import ModelRegistry
from app.services.model_evaluation_service import (
    ModelEvaluationService,
)


def setup_models():

    ModelRegistry.load_models(
        [
            {
                "model_id": "test-model",
                "display_name": "Test Model",
                "is_free": True,
            },
            {
                "model_id": "unknown-model",
                "display_name": "Unknown Model",
                "is_free": True,
            },
        ]
    )


def setup_capability():

    CapabilityEngine._profiles = {
        "test-model": {
            "model": "test-model",
            "coding": 90.0,
        }
    }


def test_evaluate_models():

    setup_models()
    setup_capability()

    results = (
        ModelEvaluationService.evaluate_models(
            task_type="coding"
        )
    )

    assert len(results) == 2

    test_model = next(
        result
        for result in results
        if result["model"] == "test-model"
    )

    assert test_model["capability_available"] is True
    assert test_model["capability_score"] == 9.0


def test_get_capable_models():

    setup_models()
    setup_capability()

    results = (
        ModelEvaluationService.get_capable_models(
            task_type="coding"
        )
    )

    assert len(results) == 1
    assert results[0]["model"] == "test-model"