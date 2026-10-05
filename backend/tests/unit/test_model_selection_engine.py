import pytest
from app.engines.capability_engine import (
    CapabilityEngine,
)
from app.engines.model_selection_engine import (
    ModelSelectionEngine,
)
from app.models.model_registry import (
    ModelRegistry,
)


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

    assert (
        result["ideal_model"]["model"]
        == "paid-model"
    )

    assert (
        result["selected_model"]["model"]
        == "free-model-a"
    )

    assert result["capability_gap"] == 0.5


def test_select_ideal_model_without_capability():

    ModelRegistry.load_models(
        [
            {
                "model_id": "unknown-model",
                "display_name": "Unknown Model",
                "is_free": False,
            }
        ]
    )

    CapabilityEngine._profiles = {}

    with pytest.raises(
        ValueError,
        match="No capability data available",
    ):
        ModelSelectionEngine.select_ideal_model(
            "coding"
        )


def test_select_best_free_model_without_capability():

    ModelRegistry.load_models(
        [
            {
                "model_id": "free-model",
                "display_name": "Free Model",
                "is_free": True,
            }
        ]
    )

    CapabilityEngine._profiles = {}

    with pytest.raises(
        ValueError,
        match="No free model with verified capability",
    ):
        ModelSelectionEngine.select_best_free_model(
            task_type="coding",
            ideal_score=9.0,
        )
def test_paid_ideal_model_uses_closest_free_model():

    candidates = [
        {
            "model": "paid-model",
            "score": 9.5,
            "capability_score": 9.5,
            "capability_available": True,
            "is_free": False,
        },
        {
            "model": "free-model-a",
            "score": 8.8,
            "capability_score": 9.0,
            "capability_available": True,
            "is_free": True,
        },
        {
            "model": "free-model-b",
            "score": 8.2,
            "capability_score": 7.5,
            "capability_available": True,
            "is_free": True,
        },
    ]

    result = (
        ModelSelectionEngine.select_from_candidates(
            candidates
        )
    )

    assert result["ideal_model"] == "paid-model"

    assert (
        result["selected_model"]
        == "free-model-a"
    )

    assert result["ideal_is_free"] is False

    assert (
        result["selected_is_free"]
        is True
    )

    assert result["capability_gap"] == 0.5

    assert (
        "paid" in result["reason"].lower()
    )

    assert (
        "free alternative"
        in result["reason"].lower()
    )