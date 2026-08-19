from app.engines.capability_engine import (
    CapabilityEngine,
)
from app.engines.model_selection_engine import (
    ModelSelectionEngine,
)
from app.models.model_registry import ModelRegistry


def setup():

    ModelRegistry.load_models(
        [
            {
                "model_id": "paid-model",
                "display_name": "Paid Model",
                "is_free": False,
            },
            {
                "model_id": "free-model-a",
                "display_name": "Free Model A",
                "is_free": True,
            },
            {
                "model_id": "free-model-b",
                "display_name": "Free Model B",
                "is_free": True,
            },
        ]
    )

    CapabilityEngine._profiles = {
        "paid-model": {
            "model": "paid-model",
            "coding": 95.0,
        },
        "free-model-a": {
            "model": "free-model-a",
            "coding": 90.0,
        },
        "free-model-b": {
            "model": "free-model-b",
            "coding": 75.0,
        },
    }


def test_select_ideal_model():

    setup()

    result = (
        ModelSelectionEngine.select_ideal_model(
            "coding"
        )
    )

    assert result["model"] == "paid-model"
    assert result["capability_score"] == 9.5


def test_select_best_free_model():

    setup()

    result = (
        ModelSelectionEngine.select_best_free_model(
            task_type="coding",
            ideal_score=9.5,
        )
    )

    assert result["model"] == "free-model-a"
    assert result["capability_score"] == 9.0


def test_select():

    setup()

    result = ModelSelectionEngine.select(
        "coding"
    )

    assert result["ideal_model"]["model"] == (
        "paid-model"
    )

    assert result["selected_model"]["model"] == (
        "free-model-a"
    )

    assert result["capability_gap"] == 0.5