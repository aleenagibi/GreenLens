"""
Chat Service

Contains the business logic for generating AI responses.
"""

from app.db.database import SessionLocal
from app.db.models import InferenceRecord
from app.engines.benchmark_engine import BenchmarkEngine
from app.engines.pipeline_engine import PipelineEngine
from app.engines.sustainability_engine import SustainabilityEngine
from app.providers.provider_factory import ProviderFactory
from app.services.model_performance_service import (
    ModelPerformanceService,
)


class ChatService:
    """
    Service responsible for coordinating AI interactions.
    """

    def __init__(self):
        self.pipeline = PipelineEngine()

    def generate_response(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict:

        candidates = [
            {
                "model": "openai/gpt-oss-20b:free",
                "estimated_tokens": max_tokens,
                "latency_score": 8.0,
            }
        ]

        pipeline_result = self.pipeline.run(
            prompt=prompt,
            models=candidates,
        )

        selected_model = (
            model
            or pipeline_result["selection"]["selected_model"]
        )

        provider = ProviderFactory.get_provider(
            "openrouter"
        )

        start_time = BenchmarkEngine.start_timer()

        try:
            response = provider.generate_response(
                prompt=prompt,
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            latency_ms = BenchmarkEngine.calculate_latency(
                start_time
            )
            ModelPerformanceService.record_latency(
                model=selected_model,
                latency_ms=latency_ms,
            )
            benchmark = BenchmarkEngine.create_result(
                response=response,
                latency_ms=latency_ms,
            )

            sustainability = SustainabilityEngine.calculate(
                total_tokens=benchmark.total_tokens,
                eco_impacts=response.get("impacts"),
            )

            response["pipeline"] = pipeline_result

            response["recommendation"] = {
                "task_type": pipeline_result["task"]["task_type"],
                "score": pipeline_result["selection"]["score"],
                "reason": pipeline_result["selection"]["reason"],
            }

            response["benchmark"] = benchmark.to_dict()

            response["sustainability"] = (
                sustainability.to_dict()
            )

            db = SessionLocal()

            try:
                record = InferenceRecord(
                    prompt=prompt,
                    provider=response["provider"],
                    model=response["model"],
                    task_type=(
                        pipeline_result["task"]["task_type"]
                    ),
                    recommendation_score=(
                        pipeline_result["selection"]["score"]
                    ),
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
                db.refresh(record)

            finally:
                db.close()

            return response

        except Exception:
            BenchmarkEngine.calculate_latency(start_time)
            raise