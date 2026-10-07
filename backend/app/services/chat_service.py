"""GreenLens routing and inference orchestration service."""

import time

from app.db.database import SessionLocal
from app.db.models import InferenceRecord
from app.engines.benchmark_engine import BenchmarkEngine
from app.engines.pipeline_engine import PipelineEngine
from app.engines.sustainability_engine import SustainabilityEngine
from app.providers.provider_factory import ProviderFactory
from app.services.model_catalog_service import ModelCatalogService
from app.services.model_performance_service import ModelPerformanceService


class ChatService:
    def __init__(self):
        self.pipeline = PipelineEngine()

    @staticmethod
    def _is_retriable_inference_error(exc: Exception) -> bool:
        error_text = str(exc).lower()
        error_type = type(exc).__name__.lower()
        markers = {
            "429", "rate limit", "ratelimit", "temporarily rate-limited",
            "upstream provider", "provider returned error",
            "temporarily unavailable", "service unavailable", "no text content",
        }
        return "ratelimit" in error_type or any(m in error_text for m in markers)

    @staticmethod
    def _get_fallback_candidates(candidates: list[dict], attempted_models: set[str]) -> list[dict]:
        return [
            candidate for candidate in candidates
            if candidate.get("is_free", False) and candidate["model"] not in attempted_models
        ]

    @staticmethod
    def _prepare_candidates(max_tokens: int) -> list[dict]:
        catalog_models = ModelCatalogService.get_chat_models()
        if not catalog_models:
            raise ValueError("No OpenRouter chat models are currently available.")
        return [
            {
                "model": item["model_id"],
                "display_name": item.get("display_name"),
                "provider": item.get("provider"),
                "prompt_price": item.get("prompt_price"),
                "completion_price": item.get("completion_price"),
                "estimated_tokens": max_tokens,
                "latency_score": 5.0,
                "is_free": item["is_free"],
                "artificial_analysis": item.get("artificial_analysis"),
            }
            for item in catalog_models
        ]

    def route(self, prompt: str, preset: str = "balanced", max_tokens: int = 512) -> dict:
        total_start = time.perf_counter()
        stage_start = time.perf_counter()
        candidates = self._prepare_candidates(max_tokens)
        print(f"[GreenLens] Model catalogue/candidates: {time.perf_counter() - stage_start:.3f}s ({len(candidates)} models)")

        stage_start = time.perf_counter()
        pipeline_result = self.pipeline.run(prompt=prompt, models=candidates, preset=preset)
        print(f"[GreenLens] Model selection pipeline: {time.perf_counter() - stage_start:.3f}s")

        selection = pipeline_result["selection"]
        explanation = pipeline_result["explanation"]
        comparison = explanation["comparison"]
        ideal_id = selection["ideal_model"]
        selected_id = selection["selected_model"]

        def candidate(model_id: str):
            return next((item for item in comparison if item["model"] == model_id), None)

        ideal_candidate = candidate(ideal_id)
        selected_candidate = candidate(selected_id)

        routing = {
            "ideal_model": ideal_id,
            "ideal_display_name": (ideal_candidate or {}).get("display_name"),
            "ideal_is_free": selection["ideal_is_free"],
            "selected_model": selected_id,
            "selected_display_name": (selected_candidate or {}).get("display_name"),
            "selected_is_free": selection["selected_is_free"],
            "capability_gap": selection["capability_gap"],
            "fit_score": selection["score"],
            "used_free_alternative": ideal_id != selected_id,
            "reason": selection["reason"],
            "summary": explanation["summary"],
            "comparison": comparison,
            "preset": preset,
            "ideal_estimated_carbon_g": (ideal_candidate or {}).get("estimated_carbon_g"),
            "selected_estimated_carbon_g": (selected_candidate or {}).get("estimated_carbon_g"),
            "selected_is_free": selection["selected_is_free"],
        }
        print(f"[GreenLens] TOTAL ROUTE: {time.perf_counter() - total_start:.3f}s")
        return {
            "task": pipeline_result["task"],
            "routing": routing,
            "pipeline": pipeline_result,
        }

    def execute(
        self,
        prompt: str,
        model: str,
        preset: str = "balanced",
        ideal_model: str | None = None,
        capability_gap: float | None = None,
        ideal_estimated_carbon_g: float | None = None,
        selected_estimated_carbon_g: float | None = None,
        selected_is_free: bool | None = None,
        task_type: str | None = None,
        fit_score: float | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict:
        candidates = self._prepare_candidates(max_tokens)
        free_ids = {c["model"] for c in candidates if c.get("is_free", False)}
        if model not in free_ids:
            raise ValueError("The requested model is not a currently available free OpenRouter chat model.")

        provider = ProviderFactory.get_provider("openrouter")
        attempted_models: set[str] = set()
        attempts: list[dict] = []
        fallback_used = False
        fallback_reason = None
        models_to_try = [model]
        fallback_candidates = self._get_fallback_candidates(candidates, {model})
        models_to_try.extend(c["model"] for c in fallback_candidates[:2])

        response = None
        actual_model = None
        start_time = None
        for candidate_model in models_to_try:
            attempted_models.add(candidate_model)
            start_time = BenchmarkEngine.start_timer()
            try:
                response = provider.generate_response(
                    prompt=prompt, model=candidate_model,
                    temperature=temperature, max_tokens=max_tokens,
                )
                if not response.get("content") or not str(response["content"]).strip():
                    raise RuntimeError(f"No text content returned by model {candidate_model}.")
                actual_model = candidate_model
                attempts.append({"model": candidate_model, "success": True})
                break
            except Exception as exc:
                attempts.append({"model": candidate_model, "success": False, "error": str(exc)})
                if not self._is_retriable_inference_error(exc):
                    raise
                fallback_used = True
                fallback_reason = str(exc)
        else:
            raise RuntimeError("All available free models failed during inference.")

        latency_ms = BenchmarkEngine.calculate_latency(start_time)
        ModelPerformanceService.record_latency(model=actual_model, latency_ms=latency_ms)
        benchmark = BenchmarkEngine.create_result(response=response, latency_ms=latency_ms)
        sustainability = SustainabilityEngine.calculate(
            total_tokens=benchmark.total_tokens, eco_impacts=response.get("impacts")
        )

        inference = {
            "selected_model": model,
            "actual_model": actual_model,
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
            "attempts": attempts,
        }
        result = {
            "provider": response["provider"],
            "model": actual_model,
            "content": response["content"],
            "usage": response.get("usage", {}),
            "benchmark": benchmark.to_dict(),
            "sustainability": sustainability.to_dict(),
            "inference": inference,
        }

        db = SessionLocal()
        try:
            record = InferenceRecord(
                prompt=prompt,
                provider=response["provider"],
                model=actual_model,
                ideal_model=ideal_model,
                capability_gap=capability_gap,
                ideal_estimated_carbon_g=ideal_estimated_carbon_g,
                selected_estimated_carbon_g=selected_estimated_carbon_g,
                fallback_used=fallback_used,
                selected_is_free=selected_is_free,
                preset=preset,
                task_type=task_type or "unknown",
                recommendation_score=fit_score if fit_score is not None else 0.0,
                latency_ms=benchmark.latency_ms,
                prompt_tokens=benchmark.prompt_tokens,
                completion_tokens=benchmark.completion_tokens,
                total_tokens=benchmark.total_tokens,
                energy_wh=sustainability.energy_wh,
                carbon_g=sustainability.carbon_g,
                green_score=sustainability.green_score,
                success=benchmark.success,
            )
            db.add(record)
            db.commit()
        finally:
            db.close()

        return result

    def generate_response(self, prompt: str, model: str | None = None, temperature: float = 0.7, max_tokens: int = 512) -> dict:
        """Backward-compatible combined endpoint: route, then execute."""
        route_result = self.route(prompt=prompt, max_tokens=max_tokens)
        routing = route_result["routing"]
        selected = model or routing["selected_model"]
        execution = self.execute(
            prompt=prompt, model=selected, max_tokens=max_tokens, temperature=temperature,
            ideal_model=routing["ideal_model"], capability_gap=routing["capability_gap"],
            ideal_estimated_carbon_g=routing["ideal_estimated_carbon_g"],
            selected_estimated_carbon_g=routing["selected_estimated_carbon_g"],
            selected_is_free=routing["selected_is_free"],
            task_type=route_result["task"]["task_type"],
            fit_score=routing["fit_score"],
        )
        execution["pipeline"] = route_result["pipeline"]
        execution["recommendation"] = {
            "task_type": route_result["task"]["task_type"],
            "score": routing["fit_score"],
            "reason": routing["reason"],
        }
        execution["routing"] = routing
        return execution
