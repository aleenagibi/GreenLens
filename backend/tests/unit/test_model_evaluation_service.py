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
                "model_id": "livebench-model",
                "display_name": "LiveBench Model",
                "is_free": True,
            },
            {
                "model_id": "artificial-analysis-model",
                "display_name": "Artificial Analysis Model",
                "is_free": True,
                "artificial_analysis": {
                    "intelligence_index": 52.6,
                    "coding_index": 68.8,
                    "agentic_index": 45.7,
                },
            },
            {
                "model_id": "unknown-model",
                "display_name": "Unknown Model",
                "is_free": True,
            },
            {
                "model_id": "paid-model",
                "display_name": "Paid Model",
                "is_free": False,
            },
        ]
    )


def setup_capability():

    CapabilityEngine._profiles = {
        "livebench-model": {
            "model": "livebench-model",
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

    assert len(results) == 4

    livebench_model = next(
        result
        for result in results
        if result["model"] == "livebench-model"
    )

    assert (
        livebench_model["capability_available"]
        is True
    )

    assert (
        livebench_model["capability_score"]
        == 9.0
    )

    assert (
        livebench_model["capability_source"]
        == "LiveBench"
    )


def test_artificial_analysis_fallback():

    setup_models()
    setup_capability()

    results = (
        ModelEvaluationService.evaluate_models(
            task_type="coding"
        )
    )

    model = next(
        result
        for result in results
        if result["model"]
        == "artificial-analysis-model"
    )

    assert (
        model["capability_available"]
        is True
    )

    assert (
        model["capability_score"]
        == 6.88
    )

    assert (
        model["capability_source"]
        == "ArtificialAnalysis"
    )


def test_unavailable_capability():

    setup_models()
    setup_capability()

    results = (
        ModelEvaluationService.evaluate_models(
            task_type="coding"
        )
    )

    model = next(
        result
        for result in results
        if result["model"]
        == "unknown-model"
    )

    assert (
        model["capability_available"]
        is False
    )

    assert (
        model["capability_score"]
        is None
    )

    assert (
        model["capability_source"]
        == "unavailable"
    )


def test_get_capable_models():

    setup_models()
    setup_capability()

    results = (
        ModelEvaluationService.get_capable_models(
            task_type="coding"
        )
    )

    model_ids = {
        result["model"]
        for result in results
    }

    assert "livebench-model" in model_ids

    assert (
        "artificial-analysis-model"
        in model_ids
    )

    assert (
        "unknown-model"
        not in model_ids
    )


def test_get_free_models_only():

    setup_models()
    setup_capability()

    results = (
        ModelEvaluationService.evaluate_models(
            task_type="coding",
            free_only=True,
        )
    )

    assert len(results) == 3

    model_ids = {
        result["model"]
        for result in results
    }

    assert "livebench-model" in model_ids

    assert (
        "artificial-analysis-model"
        in model_ids
    )

    assert "unknown-model" in model_ids

    assert "paid-model" not in model_ids


def test_get_capable_free_models_only():

    setup_models()
    setup_capability()

    results = (
        ModelEvaluationService.get_capable_models(
            task_type="coding",
            free_only=True,
        )
    )

    model_ids = {
        result["model"]
        for result in results
    }

    assert "livebench-model" in model_ids

    assert (
        "artificial-analysis-model"
        in model_ids
    )

    assert "unknown-model" not in model_ids

    assert "paid-model" not in model_ids