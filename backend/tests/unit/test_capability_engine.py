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

    result = CapabilityEngine.predict(
        "unknown-model",
        "coding",
    )

    assert result.available is False
    assert result.score is None


def test_unknown_task():

    result = CapabilityEngine.predict(
        "test-model",
        "something_unknown",
    )

    assert result.available is False
    assert result.score is None