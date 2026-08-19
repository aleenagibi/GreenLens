"""
Capability Engine

Provides model capability scores using verified
LiveBench benchmark data.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CapabilityResult:
    model: str
    task_type: str
    score: float | None
    source: str
    available: bool

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "task_type": self.task_type,
            "score": self.score,
            "source": self.source,
            "available": self.available,
        }


class CapabilityEngine:
    """
    Looks up model capability for a specific task
    using the processed LiveBench dataset.
    """

    _profiles: dict[str, dict] = {}

    CATEGORY_MAP = {
        "general": "overall",
        "reasoning": "reasoning",
        "coding": "coding",
        "mathematics": "mathematics",
        "math": "mathematics",
        "data_analysis": "data_analysis",
        "language": "language",
        "writing": "language",
        "instruction_following": "instruction_following",
        "agentic_coding": "agentic_coding",
    }

    @classmethod
    def load_profiles(
        cls,
        file_path: str | None = None,
    ) -> None:
        """
        Load processed LiveBench capability profiles.
        """

        if file_path is None:
            base_dir = Path(__file__).resolve().parents[2]

            file_path = str(
                base_dir
                / "data"
                / "benchmarks"
                / "livebench"
                / "capability_profiles.json"
            )

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Capability profiles not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            profiles = json.load(file)

        cls._profiles = {
            profile["model"]: profile
            for profile in profiles
            if profile.get("model")
        }

    @classmethod
    def predict(
        cls,
        model: str,
        task_type: str,
    ) -> CapabilityResult:
        """
        Return the LiveBench capability score for
        a model and task type.
        """

        category = cls.CATEGORY_MAP.get(
            task_type.lower()
        )

        if category is None:
            return CapabilityResult(
                model=model,
                task_type=task_type,
                score=None,
                source="unavailable",
                available=False,
            )

        profile = cls._profiles.get(model)

        if profile is None:
            return CapabilityResult(
                model=model,
                task_type=task_type,
                score=None,
                source="unavailable",
                available=False,
            )

        score = profile.get(category)

        if score is None:
            return CapabilityResult(
                model=model,
                task_type=task_type,
                score=None,
                source="unavailable",
                available=False,
            )

        # LiveBench is 0–100.
        # GreenLens uses 0–10.
        normalized_score = round(
            float(score) / 10,
            2,
        )

        return CapabilityResult(
            model=model,
            task_type=task_type,
            score=normalized_score,
            source="LiveBench",
            available=True,
        )