"""
LiveBench Integration

Provides verified LiveBench capability data
to GreenLens.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LiveBenchScore:
    model: str
    overall_score: float
    reasoning_score: float
    coding_score: float
    agentic_coding_score: float
    mathematics_score: float
    data_analysis_score: float
    language_score: float
    instruction_following_score: float


class LiveBenchIntegration:
    """
    Interface between GreenLens and LiveBench data.
    """

    _scores: dict[str, LiveBenchScore] = {}

    @classmethod
    def load_scores(
        cls,
        data: dict[str, dict[str, float]],
    ) -> None:
        """
        Load verified LiveBench scores.
        """

        cls._scores.clear()

        for model, scores in data.items():

            cls._scores[model] = LiveBenchScore(
                model=model,
                overall_score=scores["overall"],
                reasoning_score=scores["reasoning"],
                coding_score=scores["coding"],
                agentic_coding_score=scores[
                    "agentic_coding"
                ],
                mathematics_score=scores[
                    "mathematics"
                ],
                data_analysis_score=scores[
                    "data_analysis"
                ],
                language_score=scores["language"],
                instruction_following_score=scores[
                    "instruction_following"
                ],
            )

    @classmethod
    def get_score(
        cls,
        model: str,
    ) -> LiveBenchScore | None:

        return cls._scores.get(model)

    @classmethod
    def has_score(
        cls,
        model: str,
    ) -> bool:

        return model in cls._scores

    @classmethod
    def get_all(
        cls,
    ) -> dict[str, LiveBenchScore]:

        return cls._scores.copy()