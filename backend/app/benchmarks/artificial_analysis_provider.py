"""
Artificial Analysis Benchmark Provider

Retrieves current Artificial Analysis language-model
indices dynamically through the official API.

The Artificial Analysis catalogue is fetched once and
cached in memory so individual model lookups do not
trigger repeated API requests.
"""

from typing import Any

import requests

from app.benchmarks.base_provider import (
    BaseBenchmarkProvider,
    BenchmarkResult,
)
from app.core.config import settings


_API_KEY_NOT_PROVIDED = object()


class ArtificialAnalysisProvider(
    BaseBenchmarkProvider
):
    """
    Dynamic Artificial Analysis benchmark provider.

    The API catalogue is cached and indexed locally.
    """

    BASE_URL = (
        "https://artificialanalysis.ai/api/v2"
    )

    FREE_MODELS_ENDPOINT = (
        f"{BASE_URL}/language/models/free"
    )

    REQUEST_TIMEOUT = 15

    TASK_INDEX_MAP = {
        "general": (
            "artificial_analysis_intelligence_index",
            "Artificial Analysis Intelligence Index",
        ),
        "reasoning": (
            "artificial_analysis_intelligence_index",
            "Artificial Analysis Intelligence Index",
        ),
        "coding": (
            "artificial_analysis_coding_index",
            "Artificial Analysis Coding Index",
        ),
        "agentic_coding": (
            "artificial_analysis_agentic_index",
            "Artificial Analysis Agentic Index",
        ),
        "language": (
            "artificial_analysis_intelligence_index",
            "Artificial Analysis Intelligence Index",
        ),
        "writing": (
            "artificial_analysis_intelligence_index",
            "Artificial Analysis Intelligence Index",
        ),
        "instruction_following": (
            "artificial_analysis_intelligence_index",
            "Artificial Analysis Intelligence Index",
        ),
        "mathematics": (
            "artificial_analysis_intelligence_index",
            "Artificial Analysis Intelligence Index",
        ),
    }

    # --------------------------------------------------
    # In-memory cache
    # --------------------------------------------------

    _models_cache: dict[str, dict[str, Any]] | None = None

    def __init__(
        self,
        api_key: str | None | object = _API_KEY_NOT_PROVIDED,
    ):
        """
        Initialize the provider.

        If no api_key argument is supplied:
            use the key from GreenLens settings.

        If api_key=None is explicitly supplied:
            operate without an API key.
        """

        if api_key is _API_KEY_NOT_PROVIDED:

            self.api_key = getattr(
                settings,
                "ARTIFICIAL_ANALYSIS_API_KEY",
                None,
            )

        else:

            self.api_key = api_key

    def get_benchmark(
        self,
        model: str,
        task_type: str,
    ) -> BenchmarkResult | None:
        """
        Retrieve Artificial Analysis benchmark
        evidence for a model and task.

        The Artificial Analysis catalogue is fetched
        only once per application process.
        """

        if not self.api_key:
            return None

        task_key = task_type.lower()

        mapping = self.TASK_INDEX_MAP.get(
            task_key
        )

        if mapping is None:
            return None

        index_field, benchmark_name = mapping

        normalized_model = (
            self.normalize_model_id(model)
        )

        if not normalized_model:
            return None

        try:

            models = self.get_cached_models()

        except requests.RequestException:

            return None

        model_data = models.get(
            normalized_model
        )

        if model_data is None:
            return None

        evaluations = (
            model_data.get("evaluations")
            or {}
        )

        raw_score = evaluations.get(
            index_field
        )

        if raw_score is None:
            return None

        try:

            raw_score = float(raw_score)

        except (
            TypeError,
            ValueError,
        ):

            return None

        normalized_score = round(
            raw_score / 10,
            2,
        )

        return BenchmarkResult(
            model=model,
            task_type=task_type,
            benchmark=benchmark_name,
            score=normalized_score,
            source="ArtificialAnalysis",
            verified=True,
        )

    def get_cached_models(
        self,
    ) -> dict[str, dict[str, Any]]:
        """
        Return the cached Artificial Analysis model
        catalogue.

        The API is called only if the catalogue has
        not already been loaded.
        """

        if (
            ArtificialAnalysisProvider._models_cache
            is not None
        ):
            return (
                ArtificialAnalysisProvider._models_cache
            )

        models = self.fetch_models()

        indexed_models: dict[
            str,
            dict[str, Any],
        ] = {}

        for model in models:

            slug = str(
                model.get(
                    "slug",
                    "",
                )
            ).lower()

            openrouter_id = str(
                model.get(
                    "openrouter_api_id",
                    "",
                )
            ).lower()

            if slug:
                indexed_models[slug] = model

            if openrouter_id:

                indexed_models[
                    openrouter_id
                ] = model

                if "/" in openrouter_id:

                    normalized_openrouter_id = (
                        openrouter_id.split(
                            "/",
                            1,
                        )[1]
                    )

                    indexed_models[
                        normalized_openrouter_id
                    ] = model

        ArtificialAnalysisProvider._models_cache = (
            indexed_models
        )

        return indexed_models

    def fetch_models(
        self,
    ) -> list[dict[str, Any]]:
        """
        Fetch available language models from
        Artificial Analysis.

        This function is called only when the
        in-memory cache is empty.
        """

        if not self.api_key:
            return []

        headers = {
            "x-api-key": str(
                self.api_key
            ),
        }

        page = 1

        all_models: list[
            dict[str, Any]
        ] = []

        while True:

            response = requests.get(
                self.FREE_MODELS_ENDPOINT,
                headers=headers,
                params={
                    "page": page,
                },
                timeout=self.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            models = data.get(
                "data",
                [],
            )

            all_models.extend(
                models
            )

            pagination = (
                data.get("pagination")
                or {}
            )

            has_more = pagination.get(
                "has_more",
                False,
            )

            if not has_more:
                break

            page += 1

        return all_models

    @staticmethod
    def normalize_model_id(
        model: str,
    ) -> str:
        """
        Normalize an OpenRouter model ID.

        Examples:

            openai/gpt-oss-20b:free
                -> gpt-oss-20b

            z-ai/glm-5.2:free
                -> glm-5.2

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

        return normalized.lower()

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the in-memory Artificial Analysis
        catalogue cache.

        Useful for testing or forcing a refresh.
        """

        cls._models_cache = None