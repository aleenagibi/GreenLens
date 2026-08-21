"""
Benchmark Registry

Defines verified task-to-benchmark mappings used by
GreenLens when LiveBench and Artificial Analysis data
are unavailable.

This registry does NOT calculate scores.
It only defines which benchmark is appropriate for
a given task type.
"""


from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkDefinition:
    """
    Definition of a benchmark that can provide
    task-specific capability evidence.
    """

    name: str
    task_type: str
    source: str
    normalization_max: float


class BenchmarkRegistry:
    """
    Central registry of approved capability benchmarks.
    """

    _benchmarks: dict[str, list[BenchmarkDefinition]] = {
        "general": [
            BenchmarkDefinition(
                name="MMLU-Pro",
                task_type="general",
                source="vendor",
                normalization_max=100.0,
            ),
        ],
        "reasoning": [
            BenchmarkDefinition(
                name="GPQA",
                task_type="reasoning",
                source="vendor",
                normalization_max=100.0,
            ),
        ],
        "coding": [
            BenchmarkDefinition(
                name="LiveCodeBench",
                task_type="coding",
                source="vendor",
                normalization_max=100.0,
            ),
            BenchmarkDefinition(
                name="SWE-Bench",
                task_type="coding",
                source="vendor",
                normalization_max=100.0,
            ),
        ],
        "mathematics": [
            BenchmarkDefinition(
                name="AIME",
                task_type="mathematics",
                source="vendor",
                normalization_max=100.0,
            ),
            BenchmarkDefinition(
                name="MATH",
                task_type="mathematics",
                source="vendor",
                normalization_max=100.0,
            ),
        ],
        "language": [
            BenchmarkDefinition(
                name="MMLU-Pro",
                task_type="language",
                source="vendor",
                normalization_max=100.0,
            ),
        ],
        "instruction_following": [
            BenchmarkDefinition(
                name="IFEval",
                task_type="instruction_following",
                source="vendor",
                normalization_max=100.0,
            ),
        ],
        "agentic_coding": [
            BenchmarkDefinition(
                name="SWE-Bench",
                task_type="agentic_coding",
                source="vendor",
                normalization_max=100.0,
            ),
        ],
    }

    @classmethod
    def get_benchmarks(
        cls,
        task_type: str,
    ) -> list[BenchmarkDefinition]:
        """
        Return approved benchmarks for a task type.
        """

        return cls._benchmarks.get(
            task_type.lower(),
            [],
        )

    @classmethod
    def get_primary_benchmark(
        cls,
        task_type: str,
    ) -> BenchmarkDefinition | None:
        """
        Return the first approved benchmark for a task.
        """

        benchmarks = cls.get_benchmarks(
            task_type
        )

        if not benchmarks:
            return None

        return benchmarks[0]