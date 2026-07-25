from app.db.database import get_db
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.post("/")
def create_provider(
    provider: ProviderCreate,
    db: Session = Depends(get_db)
):
    db_provider = Provider(
        name=provider.name,
        model=provider.model,
        cost_per_1m_tokens=provider.cost_per_1m_tokens,
        carbon_score=provider.carbon_score,
        active=provider.active,
    )

    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)

    return db_provider