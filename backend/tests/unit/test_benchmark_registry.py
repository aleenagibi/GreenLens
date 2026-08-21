from app.engines.benchmark_registry import (
    BenchmarkRegistry,
)


def test_coding_benchmarks():

    benchmarks = BenchmarkRegistry.get_benchmarks(
        "coding"
    )

    assert len(benchmarks) >= 1

    assert benchmarks[0].name == (
        "LiveCodeBench"
    )

    assert benchmarks[0].task_type == "coding"


def test_reasoning_benchmark():

    benchmark = (
        BenchmarkRegistry.get_primary_benchmark(
            "reasoning"
        )
    )

    assert benchmark is not None
    assert benchmark.name == "GPQA"
    assert benchmark.task_type == "reasoning"


def test_mathematics_benchmark():

    benchmarks = BenchmarkRegistry.get_benchmarks(
        "mathematics"
    )

    assert len(benchmarks) >= 1

    names = [
        benchmark.name
        for benchmark in benchmarks
    ]

    assert "AIME" in names


def test_instruction_following_benchmark():

    benchmark = (
        BenchmarkRegistry.get_primary_benchmark(
            "instruction_following"
        )
    )

    assert benchmark is not None
    assert benchmark.name == "IFEval"


def test_unknown_task():

    benchmarks = BenchmarkRegistry.get_benchmarks(
        "unknown_task"
    )

    assert benchmarks == []


def test_case_insensitive_task():

    benchmark = (
        BenchmarkRegistry.get_primary_benchmark(
            "CODING"
        )
    )

    assert benchmark is not None
    assert benchmark.name == "LiveCodeBench"