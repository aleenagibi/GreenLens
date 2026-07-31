from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Abstract base class for all AI providers.
    """

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Generate an AI response.
        """
        pass