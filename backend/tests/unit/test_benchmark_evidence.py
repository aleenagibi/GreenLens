from app.engines.benchmark_evidence import (
    BenchmarkEvidence,
    BenchmarkEvidenceRegistry,
)


def setup_function():

    BenchmarkEvidenceRegistry.clear()


def test_register_and_get_evidence():

    evidence = BenchmarkEvidence(
        model="google/gemma-4-31b-it:free",
        task_type="coding",
        benchmark="LiveCodeBench",
        score=75.0,
        source="Google",
    )

    BenchmarkEvidenceRegistry.register(
        evidence
    )

    result = BenchmarkEvidenceRegistry.get(
        "google/gemma-4-31b-it:free",
        "coding",
    )

    assert result is not None
    assert result.model == (
        "google/gemma-4-31b-it:free"
    )
    assert result.benchmark == "LiveCodeBench"
    assert result.score == 75.0


def test_normalized_score():

    evidence = BenchmarkEvidence(
        model="test/model",
        task_type="coding",
        benchmark="LiveCodeBench",
        score=80.0,
        source="Test",
    )

    assert evidence.normalized_score == 8.0


def test_to_dict():

    evidence = BenchmarkEvidence(
        model="test/model",
        task_type="reasoning",
        benchmark="GPQA",
        score=70.0,
        source="Test",
    )

    result = evidence.to_dict()

    assert result["model"] == "test/model"
    assert result["task_type"] == "reasoning"
    assert result["benchmark"] == "GPQA"
    assert result["score"] == 70.0
    assert result["normalized_score"] == 7.0
    assert result["source"] == "Test"
    assert result["verified"] is True


def test_get_score():

    evidence = BenchmarkEvidence(
        model="test/model",
        task_type="mathematics",
        benchmark="AIME",
        score=90.0,
        source="Test",
    )

    BenchmarkEvidenceRegistry.register(
        evidence
    )

    score = BenchmarkEvidenceRegistry.get_score(
        "test/model",
        "mathematics",
    )

    assert score == 9.0


def test_unknown_model():

    result = BenchmarkEvidenceRegistry.get(
        "unknown/model",
        "coding",
    )

    assert result is None


def test_unknown_task():

    result = BenchmarkEvidenceRegistry.get(
        "test/model",
        "unknown",
    )

    assert result is None


def test_unverified_evidence_is_not_registered():

    evidence = BenchmarkEvidence(
        model="test/model",
        task_type="coding",
        benchmark="TestBenchmark",
        score=90.0,
        source="Test",
        verified=False,
    )

    BenchmarkEvidenceRegistry.register(
        evidence
    )

    result = BenchmarkEvidenceRegistry.get(
        "test/model",
        "coding",
    )

    assert result is None