"""Deterministic Conventional Heuristic Router (CHR) for local research only.

This module is deliberately not imported by the production application.
It ranks an already-filtered shared candidate pool and never reads carbon or
energy fields when selecting a model.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class Calibration:
    success_rate: float
    median_latency_ms: float
    sample_count: int


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def latency_performance(latency_ms: float, peer_latencies: Iterable[float]) -> float:
    """Min-max inverse latency score over the frozen eligible calibration pool."""
    values = [float(value) for value in peer_latencies if value is not None and float(value) > 0]
    if not values or latency_ms <= 0:
        raise ValueError("Positive historical latency measurements are required")
    fastest, slowest = min(values), max(values)
    if fastest == slowest:
        return 100.0
    return _clamp((slowest - latency_ms) / (slowest - fastest) * 100.0)


def select_model(
    candidates: Iterable[Mapping[str, Any]],
    calibration: Mapping[str, Calibration | Mapping[str, Any]],
    *,
    minimum_samples: int = 10,
) -> dict[str, Any]:
    """Select a model using 50% fit, 30% reliability, 20% latency.

    `candidates` must already be capability-eligible under the same rules used
    by GreenLens. Candidate fit_score is expected on a 0..100 scale.
    """
    eligible: list[tuple[Mapping[str, Any], Calibration]] = []
    for candidate in candidates:
        model_id = str(candidate.get("model_id") or candidate.get("model") or "").strip()
        raw = calibration.get(model_id)
        if not model_id or raw is None:
            continue
        stats = raw if isinstance(raw, Calibration) else Calibration(
            success_rate=float(raw["success_rate"]),
            median_latency_ms=float(raw["median_latency_ms"]),
            sample_count=int(raw["sample_count"]),
        )
        if stats.sample_count < minimum_samples or stats.median_latency_ms <= 0:
            continue
        eligible.append((candidate, stats))
    if not eligible:
        raise ValueError("No candidates have sufficient historical calibration data")

    latencies = [stats.median_latency_ms for _, stats in eligible]
    ranked = []
    for candidate, stats in eligible:
        fit = _clamp(float(candidate.get("fit_score", 0)))
        reliability = _clamp(stats.success_rate)
        latency = latency_performance(stats.median_latency_ms, latencies)
        score = 0.50 * fit + 0.30 * reliability + 0.20 * latency
        model_id = str(candidate.get("model_id") or candidate.get("model"))
        ranked.append({
            "model_id": model_id,
            "score": round(score, 4),
            "fit_score": round(fit, 4),
            "reliability_score": round(reliability, 4),
            "latency_score": round(latency, 4),
            "calibration_samples": stats.sample_count,
        })
    # Stable deterministic tie-breaker independent of input order.
    ranked.sort(key=lambda item: (-item["score"], item["model_id"].casefold()))
    return {"selected_model": ranked[0]["model_id"], "ranking": ranked,
            "selection_method": "CHR-0.1", "weights": {"fit": .5, "reliability": .3, "latency": .2}}
