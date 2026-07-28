from app.models.provider import Provider
from app.schemas.provider import ProviderCreate
from fastapi import HTTPException
from sqlalchemy.orm import Session


def create_provider(
    provider: ProviderCreate,
    db: Session
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

def get_providers(db: Session):
    return db.query(Provider).all()

def get_provider(provider_id: int, db: Session):
    provider = (
        db.query(Provider)
        .filter(Provider.id == provider_id)
        .first()
    )

    if provider is None:
        raise HTTPException(
            status_code=404,
            detail="Provider not found"
        )

    return provider

def update_provider(
    provider_id: int,
    updated_provider: ProviderCreate,
    db: Session
):
    provider = get_provider(provider_id, db)

    provider.name = updated_provider.name
    provider.model = updated_provider.model
    provider.cost_per_1m_tokens = updated_provider.cost_per_1m_tokens
    provider.carbon_score = updated_provider.carbon_score
    provider.active = updated_provider.active

    db.commit()
    db.refresh(provider)

    return provider

def delete_provider(
    provider_id: int,
    db: Session
):
    provider = get_provider(provider_id, db)

    db.delete(provider)
    db.commit()

    return {
        "message": "Provider deleted successfully"
    }