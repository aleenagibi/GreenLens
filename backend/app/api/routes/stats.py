"""Aggregate statistics for the Insights page."""

from sqlalchemy import func
from fastapi import APIRouter
from app.db.database import SessionLocal
from app.db.models import InferenceRecord

router = APIRouter(prefix="/stats", tags=["Insights"])


@router.get("")
def stats():
    db = SessionLocal()
    try:
        total = db.query(func.count(InferenceRecord.id)).scalar() or 0
        successful = db.query(func.count(InferenceRecord.id)).filter(InferenceRecord.success.is_(True)).scalar() or 0
        total_energy = db.query(func.coalesce(func.sum(InferenceRecord.energy_wh), 0.0)).scalar() or 0.0
        total_carbon = db.query(func.coalesce(func.sum(InferenceRecord.carbon_g), 0.0)).scalar() or 0.0
        avg_latency = db.query(func.coalesce(func.avg(InferenceRecord.latency_ms), 0.0)).scalar() or 0.0
        free_runs = db.query(func.count(InferenceRecord.id)).filter(InferenceRecord.selected_is_free.is_(True)).scalar() or 0
        comparable = db.query(func.count(InferenceRecord.id)).filter(InferenceRecord.ideal_estimated_carbon_g.is_not(None), InferenceRecord.selected_estimated_carbon_g.is_not(None)).scalar() or 0
        return {
            "total_requests": total,
            "successful_requests": successful,
            "total_energy_wh": round(float(total_energy), 4),
            "total_carbon_g": round(float(total_carbon), 4),
            "average_latency_ms": round(float(avg_latency), 2),
            "free_model_requests": free_runs,
            "comparable_routing_requests": comparable,
        }
    finally:
        db.close()
