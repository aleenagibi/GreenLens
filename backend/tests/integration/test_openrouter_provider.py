"""
Integration Test for OpenRouter Provider
"""

from app.providers.openrouter_provider import OpenRouterProvider


def test_openrouter_provider():

    provider = OpenRouterProvider()

    response = provider.generate_response(
        prompt="Introduce yourself in one sentence."
    )

    print("\n========== SUCCESS ==========")
    print(f"Provider : {response['provider']}")
    print(f"Model    : {response['model']}")
    print(f"Response : {response['content']}")

    print("\nToken Usage")
    print(response["usage"])

    print("=============================\n")


if __name__ == "__main__":
    test_openrouter_provider()