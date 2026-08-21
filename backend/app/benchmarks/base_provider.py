"""
Benchmark Provider Interface

Defines the common interface used by GreenLens
benchmark data providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkResult:
    """
    A verified benchmark result for a model.
    """

    model: str
    task_type: str
    benchmark: str
    score: float
    source: str
    verified: bool = True

    def normalized_score(self) -> float:
        """
        Convert a 0-100 benchmark score to GreenLens'
        0-10 capability scale.
        """

        return round(
            self.score / 10,
            2,
        )

    def to_dict(self) -> dict:
        """
        Convert the result to a dictionary.
        """

        return {
            "model": self.model,
            "task_type": self.task_type,
            "benchmark": self.benchmark,
            "score": self.score,
            "normalized_score": self.normalized_score(),
            "source": self.source,
            "verified": self.verified,
        }


class BaseBenchmarkProvider(ABC):
    """
    Base interface for all benchmark providers.
    """

    @abstractmethod
    def get_benchmark(
        self,
        model: str,
        task_type: str,
    ) -> BenchmarkResult | None:
        """
        Retrieve benchmark evidence for a model/task.

        Return None when the provider has no verified
        benchmark information.
        """
        raise NotImplementedError