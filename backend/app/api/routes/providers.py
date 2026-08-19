from app.db.database import get_db
from app.providers.provider_registry import ProviderRegistry
from app.schemas.provider import ProviderCreate, ProviderResponse
from app.services import provider_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/providers",
    tags=["Providers"],
)


@router.post("/", response_model=ProviderResponse)
def create_provider(
    provider: ProviderCreate,
    db: Session = Depends(get_db),
):
    return provider_service.create_provider(
        provider,
        db,
    )


@router.get("/", response_model=list[ProviderResponse])
def get_providers(
    db: Session = Depends(get_db),
):
    return provider_service.get_providers(db)


@router.get("/registry")
def get_registry_providers():
    """
    Return providers registered in the GreenLens provider registry.
    """

    providers = ProviderRegistry.get_all()

    return {
        "count": len(providers),
        "providers": [
            {
                "name": provider.name,
                "display_name": provider.display_name,
                "default_model": provider.default_model,
                "capabilities": {
                    "reasoning": provider.reasoning_score,
                    "coding": provider.coding_score,
                    "writing": provider.writing_score,
                    "speed": provider.speed_score,
                    "cost": provider.cost_score,
                    "sustainability": provider.sustainability_score,
                    "reliability": provider.reliability_score,
                },
                "supports_streaming": provider.supports_streaming,
                "supports_vision": provider.supports_vision,
            }
            for provider in providers.values()
        ],
    }


@router.get(
    "/{provider_id}",
    response_model=ProviderResponse,
)
def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
):
    return provider_service.get_provider(
        provider_id,
        db,
    )


@router.put(
    "/{provider_id}",
    response_model=ProviderResponse,
)
def update_provider(
    provider_id: int,
    updated_provider: ProviderCreate,
    db: Session = Depends(get_db),
):
    return provider_service.update_provider(
        provider_id,
        updated_provider,
        db,
    )


@router.delete("/{provider_id}")
def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
):
    return provider_service.delete_provider(
        provider_id,
        db,
    )