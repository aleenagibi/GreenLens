"""
Model Performance Service

Stores and retrieves runtime performance observations
for individual models.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceRecord:
    model: str
    latency_ms: float
    sample_count: int = 1


class ModelPerformanceService:

    _records: dict[str, PerformanceRecord] = {}

    @classmethod
    def record_latency(
        cls,
        model: str,
        latency_ms: float,
    ) -> None:
        """
        Record a latency observation for a model.

        Multiple observations are combined into an
        incremental average.
        """

        existing = cls._records.get(model)

        if existing is None:
            cls._records[model] = PerformanceRecord(
                model=model,
                latency_ms=latency_ms,
                sample_count=1,
            )
            return

        new_count = existing.sample_count + 1

        new_average = (
            (
                existing.latency_ms
                * existing.sample_count
            )
            + latency_ms
        ) / new_count

        cls._records[model] = PerformanceRecord(
            model=model,
            latency_ms=round(new_average, 2),
            sample_count=new_count,
        )

    @classmethod
    def get_latency(
        cls,
        model: str,
    ) -> float | None:
        """
        Return the observed average latency.
        """

        record = cls._records.get(model)

        if record is None:
            return None

        return record.latency_ms

    @classmethod
    def get_record(
        cls,
        model: str,
    ) -> PerformanceRecord | None:

        return cls._records.get(model)

    @classmethod
    def clear(cls) -> None:
        """
        Clear runtime observations.
        Useful for testing.
        """

        cls._records.clear()