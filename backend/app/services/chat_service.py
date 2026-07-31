"""
Chat Service

Contains the business logic for generating AI responses.
"""

from app.providers.openrouter_provider import OpenRouterProvider


class ChatService:
    """
    Service responsible for coordinating
    AI interactions.
    """

    def __init__(self):

        self.provider = OpenRouterProvider()

    def generate_response(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict:

        response = self.provider.generate_response(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response