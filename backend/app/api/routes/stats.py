"""Database-backed aggregate statistics for the GreenLens Insights page."""

from sqlalchemy import case, func
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.db.models import User

from app.db.database import SessionLocal
from app.db.models import InferenceRecord

router = APIRouter(prefix="/stats", tags=["Insights"])


@router.get("")
def stats(user: User = Depends(get_current_user)):
    """Return aggregates and chart-ready records from persisted inferences."""
    db = SessionLocal()
    try:
        # Every statistic is scoped to the authenticated account. Legacy rows
        # with NULL user_id are intentionally excluded rather than shared.
        owner_filter = InferenceRecord.user_id == user.id
        total = db.query(func.count(InferenceRecord.id)).filter(owner_filter).scalar() or 0
        successful = (
            db.query(func.count(InferenceRecord.id))
            .filter(owner_filter, InferenceRecord.success.is_(True))
            .scalar() or 0
        )
        total_energy = (
            db.query(func.coalesce(func.sum(InferenceRecord.energy_wh), 0.0)).filter(owner_filter, InferenceRecord.success.is_(True)).scalar()
            or 0.0
        )
        total_carbon = (
            db.query(func.coalesce(func.sum(InferenceRecord.carbon_g), 0.0)).filter(owner_filter, InferenceRecord.success.is_(True)).scalar()
            or 0.0
        )
        total_water = db.query(func.sum(InferenceRecord.water_l)).filter(owner_filter, InferenceRecord.success.is_(True)).scalar()
        water_estimated_requests = (
            db.query(func.count(InferenceRecord.id))
            .filter(owner_filter, InferenceRecord.water_l.is_not(None), InferenceRecord.success.is_(True))
            .scalar() or 0
        )
        avg_latency = (
            db.query(func.coalesce(func.avg(InferenceRecord.latency_ms), 0.0)).filter(owner_filter).scalar()
            or 0.0
        )
        free_runs = (
            db.query(func.count(InferenceRecord.id))
            .filter(owner_filter, InferenceRecord.selected_is_free.is_(True))
            .scalar() or 0
        )
        comparable = (
            db.query(func.count(InferenceRecord.id))
            .filter(
                owner_filter,
                InferenceRecord.ideal_estimated_carbon_g.is_not(None),
                InferenceRecord.selected_estimated_carbon_g.is_not(None),
                InferenceRecord.fallback_used.is_(False),
                InferenceRecord.success.is_(True),
            )
            .scalar() or 0
        )

        # Historical performance is calculated from models that actually
        # executed inference requests. Failed attempts contribute to reliability;
        # latency, energy and carbon averages use successful responses only.
        model_rows = (
            db.query(
                InferenceRecord.model,
                func.count(InferenceRecord.id).label("attempts"),
                func.sum(case((InferenceRecord.success.is_(True), 1), else_=0)).label("successes"),
                func.avg(case((InferenceRecord.success.is_(True), InferenceRecord.latency_ms), else_=None)).label("avg_latency_ms"),
                func.avg(case((InferenceRecord.success.is_(True), InferenceRecord.energy_wh), else_=None)).label("avg_energy_wh"),
                func.avg(case((InferenceRecord.success.is_(True), InferenceRecord.carbon_g), else_=None)).label("avg_carbon_g"),
            )
            .filter(owner_filter)
            .group_by(InferenceRecord.model)
            .all()
        )

        observed = [
            row for row in model_rows
            if int(row.successes or 0) > 0
        ]
        min_latency = min((float(row.avg_latency_ms) for row in observed if row.avg_latency_ms is not None and float(row.avg_latency_ms) > 0), default=None)
        min_energy = min((float(row.avg_energy_wh) for row in observed if row.avg_energy_wh is not None and float(row.avg_energy_wh) >= 0), default=None)
        min_carbon = min((float(row.avg_carbon_g) for row in observed if row.avg_carbon_g is not None and float(row.avg_carbon_g) >= 0), default=None)

        model_performance = []
        for row in observed:
            attempts = int(row.attempts or 0)
            successes = int(row.successes or 0)
            latency = float(row.avg_latency_ms) if row.avg_latency_ms is not None else None
            energy = float(row.avg_energy_wh) if row.avg_energy_wh is not None else None
            carbon = float(row.avg_carbon_g) if row.avg_carbon_g is not None else None
            model_performance.append({
                "model": row.model,
                "attempts": attempts,
                "successful_responses": successes,
                "reliability_score": round((successes / attempts) * 10, 2) if attempts else None,
                "carbon_efficiency_score": (
                    10.0 if carbon == 0 and min_carbon == 0
                    else round((min_carbon / carbon) * 10, 2) if min_carbon is not None and carbon is not None and carbon > 0
                    else None
                ),
                "energy_efficiency_score": (
                    10.0 if energy == 0 and min_energy == 0
                    else round((min_energy / energy) * 10, 2) if min_energy is not None and energy is not None and energy > 0
                    else None
                ),
                "latency_performance_score": round((min_latency / latency) * 10, 2) if min_latency is not None and latency is not None and latency > 0 else None,
                "average_carbon_g": round(carbon, 8) if carbon is not None else None,
                "average_energy_wh": round(energy, 8) if energy is not None else None,
                "average_latency_ms": round(latency, 2) if latency is not None else None,
            })

        model_performance.sort(
            key=lambda item: (item["successful_responses"], item["attempts"]),
            reverse=True,
        )
        model_performance = model_performance[:12]

        records = (
            db.query(InferenceRecord)
            .filter(owner_filter, InferenceRecord.success.is_(True))
            .order_by(InferenceRecord.created_at.desc(), InferenceRecord.id.desc())
            .limit(100)
            .all()
        )

        # Aggregate actual executed models, not browser-local chat answers.
        model_counts = (
            db.query(InferenceRecord.model, func.count(InferenceRecord.id))
            .filter(owner_filter, InferenceRecord.success.is_(True))
            .group_by(InferenceRecord.model)
            .order_by(func.count(InferenceRecord.id).desc())
            .all()
        )

        # Model/task heatmap aggregates across all successful persisted inferences.
        heatmap_rows = (
            db.query(
                InferenceRecord.model,
                InferenceRecord.task_type,
                func.count(InferenceRecord.id),
                func.avg(InferenceRecord.carbon_g),
                func.avg(InferenceRecord.latency_ms),
            )
            .filter(owner_filter, InferenceRecord.success.is_(True))
            .group_by(InferenceRecord.model, InferenceRecord.task_type)
            .order_by(InferenceRecord.model, InferenceRecord.task_type)
            .all()
        )

        avoided_expression = case(
            (
                InferenceRecord.ideal_estimated_carbon_g > InferenceRecord.selected_estimated_carbon_g,
                InferenceRecord.ideal_estimated_carbon_g - InferenceRecord.selected_estimated_carbon_g,
            ),
            else_=0.0,
        )
        avoided_carbon = (
            db.query(func.coalesce(func.sum(avoided_expression), 0.0))
            .filter(
                owner_filter,
                InferenceRecord.ideal_estimated_carbon_g.is_not(None),
                InferenceRecord.selected_estimated_carbon_g.is_not(None),
                InferenceRecord.fallback_used.is_(False),
            )
            .scalar() or 0.0
        )

        # API returns chart points oldest-to-newest for a natural timeline.
        carbon_series = [
            {
                "label": f"Inference {record.id}",
                "value": float(record.carbon_g or 0.0),
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }
            for record in reversed(records[:24])
        ]

        waterfall_totals = (
            db.query(
                func.coalesce(func.sum(InferenceRecord.ideal_estimated_carbon_g), 0.0),
                func.coalesce(func.sum(InferenceRecord.selected_estimated_carbon_g), 0.0),
                func.count(InferenceRecord.id),
            )
            .filter(
                owner_filter,
                InferenceRecord.ideal_estimated_carbon_g.is_not(None),
                InferenceRecord.selected_estimated_carbon_g.is_not(None),
                InferenceRecord.fallback_used.is_(False),
                InferenceRecord.success.is_(True),
            )
            .one()
        )

        recent_decisions = [
            {
                "id": record.id,
                "prompt": f"Inference #{record.id}",
                "provider": record.provider,
                "actual_model": record.model,
                "ideal_model": record.ideal_model,
                "capability_gap": record.capability_gap,
                "ideal_estimated_carbon_g": record.ideal_estimated_carbon_g,
                "selected_estimated_carbon_g": record.selected_estimated_carbon_g,
                "fallback_used": bool(record.fallback_used),
                "selected_is_free": record.selected_is_free,
                "preset": record.preset,
                "task_type": record.task_type,
                "fit_score": float(record.recommendation_score or 0.0),
                "latency_ms": float(record.latency_ms or 0.0),
                "energy_wh": float(record.energy_wh or 0.0),
                "carbon_g": float(record.carbon_g or 0.0),
                "water_l": float(record.water_l) if record.water_l is not None else None,
                "sustainability_source": record.sustainability_source,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }
            for record in records[:8]
        ]

        return {
            "total_requests": int(total),
            "successful_requests": int(successful),
            "total_energy_wh": round(float(total_energy), 6),
            "total_carbon_g": round(float(total_carbon), 6),
            "total_water_l": round(float(total_water), 9) if total_water is not None else None,
            "water_estimated_requests": int(water_estimated_requests),
            "avoided_carbon_g": round(float(avoided_carbon), 6),
            "average_latency_ms": round(float(avg_latency), 2),
            "free_model_requests": int(free_runs),
            "comparable_routing_requests": int(comparable),
            "model_usage": [
                {"model": model, "count": int(count)}
                for model, count in model_counts
            ],
            "model_performance": model_performance,
            "task_model_heatmap": [
                {
                    "model": model,
                    "task_type": task_type,
                    "count": int(count),
                    "average_carbon_g": round(float(avg_carbon or 0.0), 8),
                    "average_latency_ms": round(float(avg_latency or 0.0), 2),
                }
                for model, task_type, count, avg_carbon, avg_latency in heatmap_rows
            ],
            "carbon_waterfall": {
                "ideal_carbon_g": round(float(waterfall_totals[0] or 0.0), 8),
                "selected_carbon_g": round(float(waterfall_totals[1] or 0.0), 8),
                "comparable_requests": int(waterfall_totals[2] or 0),
                "savings_carbon_g": round(
                    float(waterfall_totals[0] or 0.0) - float(waterfall_totals[1] or 0.0), 8
                ),
            },
            "carbon_series": carbon_series,
            "recent_decisions": recent_decisions,
        }
    finally:
        db.close()
