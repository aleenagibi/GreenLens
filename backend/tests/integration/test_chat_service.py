"""
Integration Test for Chat Service
"""

from app.services.chat_service import ChatService
from app.services.model_catalog_service import (
    ModelCatalogService,
)


def test_chat_service():

    service = ChatService()

    response = service.generate_response(
        prompt="Explain Artificial Intelligence in two sentences."
    )

    print("\n========== SUCCESS ==========")

    print(
        f"Provider : {response['provider']}"
    )

    print(
        f"Model    : {response['model']}"
    )

    print(
        f"Response : {response['content']}"
    )

    print("\nUsage")
    print(response["usage"])

    print("\nRecommendation")
    print(
        response["recommendation"]
    )

    print("\nSustainability")
    print(
        response["sustainability"]
    )

    print("\nPipeline Selection")
    print(
        response["pipeline"]["selection"]
    )

    print("=============================\n")

    # --------------------------------------------------
    # Basic response validation
    # --------------------------------------------------

    assert response["provider"] == "OpenRouter"

    assert response["model"]

    assert response["content"]

    assert response["usage"]

    assert response["benchmark"]

    assert response["sustainability"]

    assert response["pipeline"]

    assert response["recommendation"]

    # --------------------------------------------------
    # Verify selected model is currently FREE
    # --------------------------------------------------

    free_models = (
        ModelCatalogService.get_free_chat_models()
    )

    free_model_ids = {
        model["model_id"]
        for model in free_models
    }

    assert response["model"] in free_model_ids


if __name__ == "__main__":
    test_chat_service()