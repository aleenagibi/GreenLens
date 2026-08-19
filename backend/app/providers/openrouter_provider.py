"""
OpenRouter Provider

Concrete implementation of the BaseProvider interface
using the OpenAI SDK configured for OpenRouter.
"""

from typing import Any

from ecologits import EcoLogits
from openai import OpenAI

from app.core.config import settings
from app.providers.base_provider import BaseProvider


class OpenRouterProvider(BaseProvider):
    """
    Provider responsible for communicating
    with OpenRouter.
    """

    def __init__(self):

        # Initialize EcoLogits once for the OpenAI
        # SDK instrumentation used by OpenRouter.
        EcoLogits.init(
            providers=["openai"]
        )

        self.client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )

    def generate_response(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict[str, Any]:

        if model is None:
            model = settings.DEFAULT_MODEL

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": settings.APP_NAME,
            },
        )

        return {
            "provider": "OpenRouter",
            "model": response.model,
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "impacts": response.impacts,
        }