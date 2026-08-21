"""
Benchmark Evidence

Stores verified, task-specific benchmark results for models.

This layer is responsible only for:
    1. Storing benchmark evidence.
    2. Looking up evidence for a model and task.
    3. Normalizing a verified benchmark score to 0-10.

It does not decide which model to select.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkEvidence:
    """
    Verified benchmark result for a model.
    """

    model: str
    task_type: str
    benchmark: str
    score: float
    source: str
    verified: bool = True

    @property
    def normalized_score(self) -> float:
        """
        Convert a benchmark score from 0-100
        into GreenLens' 0-10 scale.
        """

        return round(
            self.score / 10,
            2,
        )

    def to_dict(self) -> dict:
        """
        Convert evidence into a dictionary.
        """

        return {
            "model": self.model,
            "task_type": self.task_type,
            "benchmark": self.benchmark,
            "score": self.score,
            "normalized_score": self.normalized_score,
            "source": self.source,
            "verified": self.verified,
        }


class BenchmarkEvidenceRegistry:
    """
    Registry containing verified benchmark evidence.

    The registry is intentionally separate from
    BenchmarkRegistry:

    BenchmarkRegistry
        -> defines which benchmarks are appropriate.

    BenchmarkEvidenceRegistry
        -> stores actual model benchmark results.
    """

    _evidence: dict[
        tuple[str, str],
        BenchmarkEvidence,
    ] = {}

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered evidence.

        Mainly useful for tests and controlled reloads.
        """

        cls._evidence.clear()

    @classmethod
    def register(
        cls,
        evidence: BenchmarkEvidence,
    ) -> None:
        """
        Register verified benchmark evidence.
        """

        if not evidence.verified:
            return

        key = (
            evidence.model,
            evidence.task_type.lower(),
        )

        cls._evidence[key] = evidence

    @classmethod
    def get(
        cls,
        model: str,
        task_type: str,
    ) -> BenchmarkEvidence | None:
        """
        Return benchmark evidence for a model/task.
        """

        return cls._evidence.get(
            (
                model,
                task_type.lower(),
            )
        )

    @classmethod
    def get_score(
        cls,
        model: str,
        task_type: str,
    ) -> float | None:
        """
        Return the normalized 0-10 score.

        Returns None when no verified evidence exists.
        """

        evidence = cls.get(
            model=model,
            task_type=task_type,
        )

        if evidence is None:
            return None

        return evidence.normalized_score