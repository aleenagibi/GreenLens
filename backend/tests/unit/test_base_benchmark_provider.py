from app.benchmarks.base_provider import (
    BaseBenchmarkProvider,
    BenchmarkResult,
)


def test_benchmark_result_normalization():

    result = BenchmarkResult(
        model="test/model",
        task_type="coding",
        benchmark="LiveCodeBench",
        score=80.0,
        source="Test",
    )

    assert result.normalized_score() == 8.0


def test_benchmark_result_to_dict():

    result = BenchmarkResult(
        model="test/model",
        task_type="coding",
        benchmark="LiveCodeBench",
        score=80.0,
        source="Test",
    )

    data = result.to_dict()

    assert data["model"] == "test/model"
    assert data["task_type"] == "coding"
    assert data["benchmark"] == "LiveCodeBench"
    assert data["score"] == 80.0
    assert data["normalized_score"] == 8.0
    assert data["source"] == "Test"
    assert data["verified"] is True


def test_provider_interface():

    class TestProvider(BaseBenchmarkProvider):

        def get_benchmark(
            self,
            model: str,
            task_type: str,
        ):
            return BenchmarkResult(
                model=model,
                task_type=task_type,
                benchmark="TestBenchmark",
                score=75.0,
                source="Test",
            )

    provider = TestProvider()

    result = provider.get_benchmark(
        "test/model",
        "coding",
    )

    assert result is not None
    assert result.score == 75.0
    assert result.source == "Test"