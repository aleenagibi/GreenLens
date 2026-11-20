"""Aggregations for local paired CHR/GreenLens research runs."""
from __future__ import annotations
from statistics import mean, median, pstdev
from typing import Iterable, Mapping, Any


def summarise_attempts(attempts: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(attempts)
    if not rows:
        raise ValueError("At least one attempt is required")
    successful = [row for row in rows if bool(row.get("success"))]
    def values(key: str, source: list[Mapping[str, Any]]) -> list[float]:
        return [float(row[key]) for row in source if row.get(key) is not None]
    latency = values("latency_ms", successful)
    energy_all = values("energy_wh", rows)
    carbon_all = values("carbon_g", rows)
    energy_success = values("energy_wh", successful)
    carbon_success = values("carbon_g", successful)
    quality = values("quality_score", successful)
    def stats(items: list[float]) -> dict[str, float | None]:
        return {"mean": round(mean(items), 6) if items else None,
                "median": round(median(items), 6) if items else None,
                "stddev": round(pstdev(items), 6) if len(items) > 1 else 0.0 if items else None,
                "min": min(items) if items else None, "max": max(items) if items else None}
    return {
        "attempts": len(rows), "successes": len(successful),
        "reliability_percent": round(len(successful) / len(rows) * 100, 4),
        "latency_ms": stats(latency), "energy_wh_per_attempt": round(sum(energy_all) / len(rows), 8) if energy_all else None,
        "carbon_g_per_attempt": round(sum(carbon_all) / len(rows), 8) if carbon_all else None,
        "energy_wh_per_success": round(sum(energy_success) / len(successful), 8) if energy_success else None,
        "carbon_g_per_success": round(sum(carbon_success) / len(successful), 8) if carbon_success else None,
        "quality_score": stats(quality),
        "energy_provenance": sorted({str(row.get("energy_provenance", "unreported")) for row in rows}),
        "carbon_provenance": sorted({str(row.get("carbon_provenance", "unreported")) for row in rows}),
    }
