"""Live model catalogue and registered provider metadata."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.providers.provider_registry import ProviderRegistry
from app.services.model_catalog_service import ModelCatalogService

router = APIRouter(prefix="/catalog", tags=["Catalogue"])


@router.get("")
def get_catalog():
    """Expose model and provider metadata from backend-owned sources."""
    try:
        models = ModelCatalogService.get_chat_models()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="The live OpenRouter model catalogue is temporarily unavailable.",
        ) from exc

    providers = []
    for provider in ProviderRegistry.get_all().values():
        providers.append({
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
        })

    return {
        "source": "OpenRouter model catalogue",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "model_count": len(models),
        "models": [
            {
                "model_id": model["model_id"],
                "display_name": model.get("display_name"),
                "provider": model.get("provider"),
                "context_length": model.get("context_length"),
                "is_free": model.get("is_free", False),
                "prompt_price": model.get("prompt_price"),
                "completion_price": model.get("completion_price"),
                "input_modalities": model.get("input_modalities", []),
                "output_modalities": model.get("output_modalities", []),
                "supports_reasoning": model.get("supports_reasoning", False),
            }
            for model in models
        ],
        "providers": providers,
    }
