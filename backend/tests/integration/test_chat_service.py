"""
Integration Test for Chat Service
"""

from app.services.chat_service import ChatService


def test_chat_service():

    service = ChatService()

    response = service.generate_response(
        prompt="Explain Artificial Intelligence in two sentences."
    )

    print("\n========== SUCCESS ==========")

    print(f"Provider : {response['provider']}")
    print(f"Model    : {response['model']}")
    print(f"Response : {response['content']}")

    print("\nUsage")
    print(response["usage"])

    print("=============================\n")


if __name__ == "__main__":
    test_chat_service()