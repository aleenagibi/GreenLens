from app.services.model_catalog_service import (
    ModelCatalogService,
)
from app.engines.capability_engine import (
    CapabilityEngine,
)


# Load verified LiveBench profiles first
CapabilityEngine.load_profiles()


models = ModelCatalogService.get_free_chat_models()

print(f"Free chat models: {len(models)}")
print()

livebench_count = 0
aa_count = 0
unavailable_count = 0

for i, model in enumerate(models, start=1):

    result = CapabilityEngine.predict(
        model=model["model_id"],
        task_type="general",
        model_metadata=model,
    )

    if result.source == "LiveBench":
        livebench_count += 1

    elif result.source == "ArtificialAnalysis":
        aa_count += 1

    else:
        unavailable_count += 1

    print(
        f"{i}. {model['model_id']} | "
        f"source={result.source} | "
        f"score={result.score}"
    )

print()
print("--------------------------------")
print(f"LiveBench: {livebench_count}")
print(f"Artificial Analysis: {aa_count}")
print(f"Unavailable: {unavailable_count}")
print("--------------------------------")