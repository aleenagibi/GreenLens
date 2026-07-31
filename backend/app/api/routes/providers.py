from app.db.database import get_db
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderResponse
from app.services import provider_service
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/providers", tags=["Providers"])

@router.post("/", response_model=ProviderResponse)
def create_provider(
    provider: ProviderCreate,
    db: Session = Depends(get_db)
):
    return provider_service.create_provider(provider, db)

@router.get("/", response_model=list[ProviderResponse])
def get_providers(db: Session = Depends(get_db)):
    return provider_service.get_providers(db)

@router.get("/{provider_id}", response_model=ProviderResponse)
def get_provider(
    provider_id: int,
    db: Session = Depends(get_db)
):
    return provider_service.get_provider(provider_id, db)

@router.put("/{provider_id}", response_model=ProviderResponse)
def update_provider(
    provider_id: int,
    updated_provider: ProviderCreate,
    db: Session = Depends(get_db)
):
    return provider_service.update_provider(
        provider_id,
        updated_provider,
        db
    )

@router.delete("/{provider_id}")
def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db)
):
    return provider_service.delete_provider(
        provider_id,
        db
    )