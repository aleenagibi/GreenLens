import json

from app.engines.capability_engine import (
    CapabilityEngine,
)


def test_capability_from_livebench(tmp_path):

    profiles = [
        {
            "model": "test-model",
            "reasoning": 80.0,
            "coding": 90.0,
            "mathematics": 70.0,
            "data_analysis": 75.0,
            "language": 85.0,
            "instruction_following": 80.0,
            "agentic_coding": 88.0,
            "overall": 81.0,
            "source": "LiveBench",
            "release": "2026-06-25",
        }
    ]

    file_path = tmp_path / "profiles.json"

    file_path.write_text(
        json.dumps(profiles),
        encoding="utf-8",
    )

    CapabilityEngine.load_profiles(
        str(file_path)
    )

    result = CapabilityEngine.predict(
        "test-model",
        "coding",
    )

    assert result.available is True
    assert result.score == 9.0
    assert result.source == "LiveBench"


def test_unknown_model():

    CapabilityEngine._profiles = {}

    result = CapabilityEngine.predict(
        "unknown-model",
        "coding",
    )

    assert result.available is False
    assert result.score is None
    assert result.source == "unavailable"


def test_unknown_task():

    result = CapabilityEngine.predict(
        "test-model",
        "something_unknown",
    )

    assert result.available is False
    assert result.score is None
    assert result.source == "unavailable"


def test_normalize_openrouter_free_model_id():

    result = CapabilityEngine.normalize_model_id(
        "z-ai/glm-5.2:free"
    )

    assert result == "glm-5.2"


def test_normalize_openrouter_paid_model_id():

    result = CapabilityEngine.normalize_model_id(
        "openai/gpt-5.2"
    )

    assert result == "gpt-5.2"


def test_normalize_livebench_model_id():

    result = CapabilityEngine.normalize_model_id(
        "glm-5.2"
    )

    assert result == "glm-5.2"


def test_predict_openrouter_model_with_livebench_match():

    CapabilityEngine._profiles = {
        "glm-5.2": {
            "model": "glm-5.2",
            "overall": 80.0,
            "coding": 85.0,
        }
    }

    metadata = {
        "artificial_analysis": {
            "intelligence_index": 60.0,
            "coding_index": 70.0,
        }
    }

    result = CapabilityEngine.predict(
        "z-ai/glm-5.2:free",
        "general",
        model_metadata=metadata,
    )

    assert result.model == (
        "z-ai/glm-5.2:free"
    )

    assert result.score == 8.0

    assert result.source == "LiveBench"

    assert result.available is True


def test_artificial_analysis_fallback():

    CapabilityEngine._profiles = {}

    metadata = {
        "artificial_analysis": {
            "intelligence_index": 52.6,
            "coding_index": 68.8,
            "agentic_index": 45.7,
        }
    }

    result = CapabilityEngine.predict(
        "openai/gpt-oss-20b:free",
        "general",
        model_metadata=metadata,
    )

    assert result.model == (
        "openai/gpt-oss-20b:free"
    )

    assert result.score == 5.26

    assert result.source == (
        "ArtificialAnalysis"
    )

    assert result.available is True


def test_artificial_analysis_coding():

    CapabilityEngine._profiles = {}

    metadata = {
        "artificial_analysis": {
            "intelligence_index": 52.6,
            "coding_index": 68.8,
            "agentic_index": 45.7,
        }
    }

    result = CapabilityEngine.predict(
        "openai/gpt-oss-20b:free",
        "coding",
        model_metadata=metadata,
    )

    assert result.score == 6.88

    assert result.source == (
        "ArtificialAnalysis"
    )

    assert result.available is True


def test_artificial_analysis_agentic_coding():

    CapabilityEngine._profiles = {}

    metadata = {
        "artificial_analysis": {
            "intelligence_index": 52.6,
            "coding_index": 68.8,
            "agentic_index": 45.7,
        }
    }

    result = CapabilityEngine.predict(
        "openai/gpt-oss-20b:free",
        "agentic_coding",
        model_metadata=metadata,
    )

    assert result.score == 4.57

    assert result.source == (
        "ArtificialAnalysis"
    )

    assert result.available is True


def test_no_livebench_or_artificial_analysis():

    CapabilityEngine._profiles = {}

    result = CapabilityEngine.predict(
        "openai/gpt-oss-20b:free",
        "general",
        model_metadata={
            "artificial_analysis": None
        },
    )

    assert result.available is False

    assert result.score is None

    assert result.source == "unavailable"


def test_artificial_analysis_missing_field():

    CapabilityEngine._profiles = {}

    metadata = {
        "artificial_analysis": {
            "coding_index": 68.8,
        }
    }

    result = CapabilityEngine.predict(
        "openai/gpt-oss-20b:free",
        "general",
        model_metadata=metadata,
    )

    assert result.available is False

    assert result.score is None

    assert result.source == "unavailable"