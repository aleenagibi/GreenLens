from app.services.model_catalog_service import (
    ModelCatalogService,
)


models = ModelCatalogService.get_free_chat_models()

print(f"Free chat models: {len(models)}")
print()

for i, model in enumerate(models, start=1):
    print(
        f"{i}. {model['model_id']} | "
        f"{model['display_name']} | "
        f"provider={model['provider']} | "
        f"context={model['context_length']} | "
        f"reasoning={model['supports_reasoning']}"
    )