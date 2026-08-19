"""
Benchmark Engine

Collects operational metrics from AI inference requests.
"""

from dataclasses import dataclass
from time import perf_counter
from typing import Any


@dataclass
class BenchmarkResult:
    """
    Benchmark information for a single inference request.
    """

    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    provider: str
    model: str
    success: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "provider": self.provider,
            "model": self.model,
            "success": self.success,
        }


class BenchmarkEngine:
    """
    Measures and records inference performance.
    """

    @staticmethod
    def start_timer() -> float:
        """Start an inference timer."""
        return perf_counter()

    @staticmethod
    def calculate_latency(start_time: float) -> float:
        """Calculate elapsed inference time in milliseconds."""
        return round(
            (perf_counter() - start_time) * 1000,
            2,
        )

    @staticmethod
    def create_result(
        response: dict[str, Any],
        latency_ms: float,
        success: bool = True,
    ) -> BenchmarkResult:
        """Create a benchmark result from an AI response."""

        usage = response.get("usage", {})

        return BenchmarkResult(
            latency_ms=latency_ms,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            provider=response.get("provider", "unknown"),
            model=response.get("model", "unknown"),
            success=success,
        )