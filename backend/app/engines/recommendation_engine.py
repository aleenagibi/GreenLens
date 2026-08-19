"""
Recommendation Engine

Selects the most suitable AI provider based on
the characteristics of the user's request.
"""

from app.providers.provider_registry import (
    ProviderMetadata,
    ProviderRegistry,
)


class RecommendationEngine:
    """
    Responsible for evaluating registered providers
    and recommending the most suitable provider.
    """

    @staticmethod
    def _detect_task_type(prompt: str) -> str:
        """
        Determine the approximate task type from the prompt.
        """

        text = prompt.lower()

        coding_keywords = {
            "code",
            "coding",
            "program",
            "programming",
            "python",
            "javascript",
            "debug",
            "function",
            "algorithm",
            "sql",
        }

        reasoning_keywords = {
            "reason",
            "analyze",
            "analysis",
            "solve",
            "calculate",
            "logic",
            "explain why",
            "compare",
        }

        writing_keywords = {
            "write",
            "essay",
            "article",
            "story",
            "email",
            "summarize",
            "rewrite",
            "creative",
        }

        if any(keyword in text for keyword in coding_keywords):
            return "coding"

        if any(keyword in text for keyword in reasoning_keywords):
            return "reasoning"

        if any(keyword in text for keyword in writing_keywords):
            return "writing"

        return "general"

    @staticmethod
    def _calculate_score(
        provider: ProviderMetadata,
        task_type: str,
    ) -> float:
        """
        Calculate a provider suitability score.
        """

        task_scores = {
            "coding": provider.coding_score,
            "reasoning": provider.reasoning_score,
            "writing": provider.writing_score,
            "general": (
                provider.reasoning_score
                + provider.coding_score
                + provider.writing_score
            )
            / 3,
        }

        task_score = task_scores[task_type]

        return (
            task_score * 0.40
            + provider.speed_score * 0.15
            + provider.cost_score * 0.15
            + provider.sustainability_score * 0.15
            + provider.reliability_score * 0.15
        )

    @classmethod
    def recommend(cls, prompt: str) -> dict:
        """
        Recommend the most suitable provider for a prompt.
        """

        task_type = cls._detect_task_type(prompt)

        providers = ProviderRegistry.get_all()

        if not providers:
            raise RuntimeError("No AI providers are registered.")

        scored_providers = []

        for provider in providers.values():
            score = cls._calculate_score(
                provider,
                task_type,
            )

            scored_providers.append(
                {
                    "provider": provider,
                    "score": round(score, 2),
                }
            )

        best = max(
            scored_providers,
            key=lambda item: item["score"],
        )

        selected_provider: ProviderMetadata = best["provider"]

        return {
            "provider": selected_provider.name,
            "display_name": selected_provider.display_name,
            "model": selected_provider.default_model,
            "task_type": task_type,
            "score": best["score"],
            "reason": (
                f"{selected_provider.display_name} was selected "
                f"for a {task_type} task based on its capability, "
                "speed, cost, sustainability, and reliability scores."
            ),
        }