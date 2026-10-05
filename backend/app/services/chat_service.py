"""

Chat Service



Coordinates:

1. Dynamic OpenRouter model discovery

2. GreenLens model selection

3. Actual LLM inference

4. Performance measurement

5. Sustainability measurement

6. Database logging

"""

import time


from app.db.database import SessionLocal

from app.db.models import InferenceRecord

from app.engines.benchmark_engine import BenchmarkEngine

from app.engines.pipeline_engine import PipelineEngine

from app.engines.sustainability_engine import SustainabilityEngine

from app.providers.provider_factory import ProviderFactory

from app.services.model_catalog_service import (
    ModelCatalogService,
)

from app.services.model_performance_service import (
    ModelPerformanceService,
)


class ChatService:
    """

    Service responsible for coordinating AI interactions.

    """

    def __init__(self):

        self.pipeline = PipelineEngine()

    @staticmethod
    def _is_retriable_inference_error(exc: Exception) -> bool:
        """

        Determine whether an inference failure is likely temporary

        and safe to retry with another free model.

        """

        error_text = str(exc).lower()

        error_type = type(exc).__name__.lower()

        retriable_markers = {
            "429",
            "rate limit",
            "ratelimit",
            "temporarily rate-limited",
            "upstream provider",
            "provider returned error",
            "temporarily unavailable",
            "service unavailable",
            "no text content",
        }

        if "ratelimit" in error_type:

            return True

        return any(marker in error_text for marker in retriable_markers)

    @staticmethod
    def _get_fallback_candidates(
        candidates: list[dict],
        attempted_models: set[str],
    ) -> list[dict]:
        """

        Return free models ordered by GreenLens score.



        Already-attempted models are excluded.

        """

        return [
            candidate
            for candidate in candidates
            if candidate.get("is_free", False)
            and candidate["model"] not in attempted_models
        ]

    def generate_response(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict:
        try:
            # ==================================================

            # 1. GET CURRENT OPENROUTER CHAT MODELS

            # ==================================================

            total_start = time.perf_counter()

            stage_start = time.perf_counter()

            catalog_models = ModelCatalogService.get_chat_models()

            print(
                f"[GreenLens] Model catalogue: "
                f"{time.perf_counter() - stage_start:.3f}s "
                f"({len(catalog_models)} models)"
            )

            if not catalog_models:

                raise ValueError("No OpenRouter chat models are currently available.")

            # ==================================================

            # 2. PREPARE PIPELINE CANDIDATES

            # ==================================================

            stage_start = time.perf_counter()

            candidates = []

            for catalog_model in catalog_models:

                candidates.append(
                    {
                        "model": catalog_model["model_id"],
                        "display_name": catalog_model.get("display_name"),
                        "provider": catalog_model.get("provider"),
                        "prompt_price": catalog_model.get("prompt_price"),
                        "completion_price": catalog_model.get("completion_price"),
                        "estimated_tokens": max_tokens,
                        # Level-1 latency prior.
                        #
                        # Actual latency is measured after
                        # inference by BenchmarkEngine.
                        "latency_score": 5.0,
                        # Preserve whether the model is free.
                        # ModelSelectionEngine uses this to
                        # prevent paid models from being selected
                        # for actual inference.
                        "is_free": catalog_model["is_free"],
                        # Preserve benchmark metadata so
                        # CapabilityEngine can use
                        # Artificial Analysis when
                        # LiveBench is unavailable.
                        "artificial_analysis": (
                            catalog_model.get("artificial_analysis")
                        ),
                    }
                )

            print(
                f"[GreenLens] Candidate preparation: "
                f"{time.perf_counter() - stage_start:.3f}s "
                f"({len(candidates)} candidates)"
            )

            # ==================================================

            # 3. RUN GREENLENS SELECTION PIPELINE

            # ==================================================

            stage_start = time.perf_counter()

            pipeline_result = self.pipeline.run(
                prompt=prompt,
                models=candidates,
            )

            print(
                f"[GreenLens] Model selection pipeline: "
                f"{time.perf_counter() - stage_start:.3f}s"
            )

            selected_model = pipeline_result["selection"]["selected_model"]

            # ==================================================

            # 4. OPTIONAL EXPLICIT MODEL

            # ==================================================

            #

            # We deliberately do NOT allow an arbitrary paid

            # model to bypass GreenLens selection.

            #

            # If a caller supplies a model, it must be one

            # of the currently available FREE chat models.

            #

            if model is not None:

                free_model_ids = {
                    candidate["model"]
                    for candidate in candidates
                    if candidate.get("is_free", False)
                }

                if model not in free_model_ids:

                    raise ValueError(
                        "The requested model is not a "
                        "currently available free OpenRouter "
                        "chat model."
                    )

                selected_model = model

            # ==================================================

            # 5. GET PROVIDER

            # ==================================================

            provider = ProviderFactory.get_provider("openrouter")

            # ==================================================

            # 6. ACTUAL MODEL INFERENCE

            # ==================================================

            attempted_models = set()

            inference_fallback_used = False

            inference_fallback_reason = None

            inference_attempts = []

            # Explicitly requested models should not silently change.

            allow_inference_fallback = model is None

            # Initial GreenLens-selected model

            models_to_try = [selected_model]

            if allow_inference_fallback:

                fallback_candidates = self._get_fallback_candidates(
                    candidates=candidates,
                    attempted_models={selected_model},
                )

                MAX_FALLBACK_ATTEMPTS = 2

                models_to_try.extend(
                    candidate["model"]
                    for candidate in fallback_candidates[:MAX_FALLBACK_ATTEMPTS]
                )

            response = None

            actual_model = None

            start_time = None

            for candidate_model in models_to_try:

                attempted_models.add(candidate_model)

                start_time = BenchmarkEngine.start_timer()

                inference_start = time.perf_counter()

                print(f"[GreenLens] Attempting inference with: " f"{candidate_model}")

                try:

                    response = provider.generate_response(
                        prompt=prompt,
                        model=candidate_model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    content = response.get("content")

                    if not content or not str(content).strip():
                        raise RuntimeError(
                            f"No text content returned by model {candidate_model}."
                        )
                    actual_model = candidate_model

                    inference_attempts.append(
                        {
                            "model": candidate_model,
                            "success": True,
                        }
                    )

                    print(
                        f"[GreenLens] LLM inference: "
                        f"{time.perf_counter() - inference_start:.3f}s"
                    )

                    break

                except Exception as exc:

                    inference_attempts.append(
                        {
                            "model": candidate_model,
                            "success": False,
                            "error": str(exc),
                        }
                    )

                    print(
                        f"[GreenLens] Inference failed for " f"{candidate_model}: {exc}"
                    )

                    # If this isn't a temporary/provider availability

                    # problem, do not hide the real error.

                    if not self._is_retriable_inference_error(exc):

                        raise

                    # Explicit model requests must not silently switch.

                    if not allow_inference_fallback:

                        raise

                    inference_fallback_used = True

                    inference_fallback_reason = str(exc)

                    print(f"[GreenLens] Trying next free model...")

            else:

                raise RuntimeError("All available free models failed during inference.")

            # ==================================================

            # 7. MEASURE ACTUAL LATENCY

            # ==================================================

            latency_ms = BenchmarkEngine.calculate_latency(start_time)

            ModelPerformanceService.record_latency(
                model=actual_model,
                latency_ms=latency_ms,
            )

            # ==================================================

            # 8. CREATE BENCHMARK RESULT

            # ==================================================

            benchmark = BenchmarkEngine.create_result(
                response=response,
                latency_ms=latency_ms,
            )

            # ==================================================

            # 9. CALCULATE SUSTAINABILITY

            # ==================================================

            stage_start = time.perf_counter()

            sustainability = SustainabilityEngine.calculate(
                total_tokens=(benchmark.total_tokens),
                eco_impacts=response.get("impacts"),
            )

            print(
                f"[GreenLens] Sustainability: "
                f"{time.perf_counter() - stage_start:.3f}s"
            )

            # ==================================================

            # 10. ATTACH GREENLENS METADATA

            # ==================================================

            response["pipeline"] = pipeline_result

            response["recommendation"] = {
                "task_type": (pipeline_result["task"]["task_type"]),
                "score": (pipeline_result["selection"]["score"]),
                "reason": (pipeline_result["selection"]["reason"]),
            }
            response["inference"] = {
                "selected_model": selected_model,
                "actual_model": actual_model,
                "fallback_used": inference_fallback_used,
                "fallback_reason": inference_fallback_reason,
                "attempts": inference_attempts,
            }
            response["benchmark"] = benchmark.to_dict()

            response["sustainability"] = sustainability.to_dict()

            # ==================================================

            # 11. FRONTEND-FRIENDLY ROUTING CONTRACT

            # ==================================================

            selection = pipeline_result["selection"]

            explanation = pipeline_result["explanation"]

            ideal_model_id = selection["ideal_model"]

            selected_model_id = selection["selected_model"]

            comparison = explanation["comparison"]

            response["routing"] = {
                "ideal_model": ideal_model_id,
                "ideal_display_name": next(
                    (
                        item.get("display_name")
                        for item in comparison
                        if item["model"] == ideal_model_id
                    ),
                    None,
                ),
                "ideal_is_free": selection["ideal_is_free"],
                "selected_model": selected_model_id,
                "selected_display_name": next(
                    (
                        item.get("display_name")
                        for item in comparison
                        if item["model"] == selected_model_id
                    ),
                    None,
                ),
                "selected_is_free": selection["selected_is_free"],
                "capability_gap": selection["capability_gap"],
                "fit_score": selection["score"],
                "used_free_alternative": (ideal_model_id != selected_model_id),
                "reason": selection["reason"],
                "summary": explanation["summary"],
                "comparison": comparison[:5],
            }

            # ==================================================

            # 12. DATABASE LOGGING

            # ==================================================

            db = SessionLocal()

            try:

                record = InferenceRecord(
                    prompt=prompt,
                    provider=response["provider"],
                    model=response["model"],
                    task_type=(pipeline_result["task"]["task_type"]),
                    recommendation_score=(pipeline_result["selection"]["score"]),
                    latency_ms=(benchmark.latency_ms),
                    prompt_tokens=(benchmark.prompt_tokens),
                    completion_tokens=(benchmark.completion_tokens),
                    total_tokens=(benchmark.total_tokens),
                    energy_wh=(sustainability.energy_wh),
                    carbon_g=(sustainability.carbon_g),
                    green_score=(sustainability.green_score),
                    success=(benchmark.success),
                )

                db.add(record)

                db.commit()

                db.refresh(record)

            finally:

                db.close()

            print(f"[GreenLens] TOTAL: " f"{time.perf_counter() - total_start:.3f}s")

            return response

        except Exception:
            raise
