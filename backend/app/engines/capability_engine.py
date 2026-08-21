"""
Capability Engine

Provides model capability scores using verified benchmark data.

Capability source priority:

1. LiveBench
2. Artificial Analysis
3. Unavailable

OpenRouter model IDs are normalized before matching
against LiveBench profiles.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.benchmarks.artificial_analysis_provider import (
    ArtificialAnalysisProvider,
)


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
    Determines model capability using verified benchmark data.

    Priority:

        LiveBench
            ↓
        Artificial Analysis
            ↓
        Unavailable
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

            base_dir = (
                Path(__file__).resolve().parents[2]
            )

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

    @staticmethod
    def normalize_model_id(
        model: str,
    ) -> str:
        """
        Normalize an OpenRouter model ID.

        Examples:

            z-ai/glm-5.2:free
            -> glm-5.2

            openai/gpt-oss-20b:free
            -> gpt-oss-20b

            glm-5.2
            -> glm-5.2
        """

        normalized = model.strip()

        if "/" in normalized:

            normalized = normalized.split(
                "/",
                1,
            )[1]

        if normalized.endswith(":free"):

            normalized = normalized[
                :-len(":free")
            ]

        return normalized

    @classmethod
    def predict(
        cls,
        model: str,
        task_type: str,
        model_metadata: dict[str, Any] | None = None,
    ) -> CapabilityResult:
        """
        Determine capability using:

        1. LiveBench
        2. Artificial Analysis
        3. Unavailable

        LiveBench is checked first.

        If LiveBench has no data, Artificial Analysis
        is queried dynamically.

        The original OpenRouter model ID is preserved.
        """

        task_key = task_type.lower()

        category = cls.CATEGORY_MAP.get(
            task_key
        )

        if category is None:

            return cls._unavailable_result(
                model,
                task_type,
            )

        normalized_model = (
            cls.normalize_model_id(model)
        )

        # ==================================================
        # 1. PRIMARY SOURCE: LIVEBENCH
        # ==================================================

        profile = cls._profiles.get(
            normalized_model
        )

        if profile is not None:

            score = profile.get(category)

            if score is not None:

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

        # ==================================================
        # 2. FALLBACK: ARTIFICIAL ANALYSIS
        # ==================================================

        # First check whether the model catalogue already
        # contains Artificial Analysis data.
        #
        # This preserves your existing functionality and
        # avoids an unnecessary API request when data is
        # already available.
        if model_metadata is not None:

            artificial_analysis = (
                model_metadata.get(
                    "artificial_analysis"
                )
            )

            cached_score = (
                cls._get_artificial_analysis_score(
                    artificial_analysis,
                    task_key,
                )
            )

            if cached_score is not None:

                return CapabilityResult(
                    model=model,
                    task_type=task_type,
                    score=cached_score,
                    source="ArtificialAnalysis",
                    available=True,
                )

        # If the catalogue does not contain AA data,
        # query the dynamic Artificial Analysis provider.
        provider = ArtificialAnalysisProvider()

        benchmark = provider.get_benchmark(
            model=model,
            task_type=task_type,
        )

        if benchmark is not None:

            return CapabilityResult(
                model=model,
                task_type=task_type,
                score=benchmark.score,
                source=benchmark.source,
                available=benchmark.verified,
            )

        # ==================================================
        # 3. NO VERIFIED DATA
        # ==================================================

        return cls._unavailable_result(
            model,
            task_type,
        )

    @staticmethod
    def _get_artificial_analysis_score(
        artificial_analysis: Any,
        task_type: str,
    ) -> float | None:
        """
        Extract an Artificial Analysis capability score
        from already available model metadata.

        Artificial Analysis indices are represented on a
        0–100 scale and GreenLens uses 0–10.
        """

        if not isinstance(
            artificial_analysis,
            dict,
        ):

            return None

        field_map = {
            "general": "intelligence_index",
            "reasoning": "intelligence_index",
            "coding": "coding_index",
            "agentic_coding": "agentic_index",
            "mathematics": "intelligence_index",
            "math": "intelligence_index",
            "data_analysis": "intelligence_index",
            "language": "intelligence_index",
            "writing": "intelligence_index",
            "instruction_following": (
                "intelligence_index"
            ),
        }

        field = field_map.get(
            task_type
        )

        if field is None:

            return None

        value = artificial_analysis.get(
            field
        )

        if value is None:

            return None

        try:

            value = float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None

        if value < 0:

            return None

        normalized_score = value / 10

        return round(
            max(
                0.0,
                min(
                    10.0,
                    normalized_score,
                ),
            ),
            2,
        )

    @staticmethod
    def _unavailable_result(
        model: str,
        task_type: str,
    ) -> CapabilityResult:
        """
        Return a capability result when no verified
        benchmark information is available.
        """

        return CapabilityResult(
            model=model,
            task_type=task_type,
            score=None,
            source="unavailable",
            available=False,
        )