"""
Pre-Inference Sustainability Engine

Estimates the environmental impact of an LLM request before inference.

EcoLogits 0.11.1 is used for model-specific estimation when the model
exists in its model repository.

Post-inference sustainability remains handled by SustainabilityEngine
using the realized EcoLogits impacts attached to the actual response.
"""

from dataclasses import dataclass

from ecologits.model_repository import ModelRepository
from ecologits.tracers.utils import llm_impacts

from app.engines.carbon_engine import CarbonEngine


@dataclass(frozen=True)
class PreInferenceSustainabilityResult:
    energy_wh: float
    carbon_g: float
    green_score: float
    source: str
    available: bool

    def to_dict(self) -> dict:
        return {
            "energy_wh": self.energy_wh,
            "carbon_g": self.carbon_g,
            "green_score": self.green_score,
            "source": self.source,
            "available": self.available,
        }


class PreInferenceSustainabilityEngine:

    _repository: ModelRepository | None = None

    @classmethod
    def _get_repository(cls) -> ModelRepository:
        """
        Load the EcoLogits model repository once and reuse it.
        """

        if cls._repository is None:
            cls._repository = ModelRepository.from_json()

        return cls._repository

    @classmethod
    def _find_model(cls, model_id: str):
        """
        Find an OpenRouter model in the EcoLogits repository.

        OpenRouter format:

            provider/model-name

        EcoLogits format:

            provider + model_name
        """

        if "/" not in model_id:
            return None

        provider, model_name = model_id.split("/", 1)

        repository = cls._get_repository()

        # First try exact provider + model match.
        model = repository.find_model(
            provider=provider,
            model_name=model_name,
        )

        if model is not None:
            return model

        # Fallback: match only by model name.
        #
        # This handles cases where OpenRouter and EcoLogits
        # use slightly different provider naming.
        for candidate in repository.list_models():

            if candidate.name == model_name:
                return candidate

        return None

    @classmethod
    def estimate(
        cls,
        model: str,
        prompt: str,
        complexity_score: float,
        estimated_output_tokens: int,
        model_metadata: dict | None = None,
    ) -> PreInferenceSustainabilityResult:

        # ---------------------------------------------------------
        # 1. Find model in EcoLogits repository
        # ---------------------------------------------------------

        try:
            ecologits_model = cls._find_model(model)
        except Exception:
            ecologits_model = None

        # ---------------------------------------------------------
        # 2. If EcoLogits does not know the model, use fallback
        # ---------------------------------------------------------

        if ecologits_model is None:
            return cls._fallback(
                estimated_output_tokens
            )

        # ---------------------------------------------------------
        # 3. Get EcoLogits deployment information
        # ---------------------------------------------------------

        deployment = ecologits_model.deployment

        tps = None
        ttft = None

        if deployment is not None:

            tps = getattr(
                deployment,
                "tps",
                None,
            )

            ttft = getattr(
                deployment,
                "ttft",
                None,
            )

        # ---------------------------------------------------------
        # 4. Estimate request latency
        # ---------------------------------------------------------
        #
        # EcoLogits requires request_latency.
        #
        # Before inference we cannot know the actual latency.
        #
        # EcoLogits gives us model deployment TPS and TTFT,
        # therefore:
        #
        # estimated latency =
        #       TTFT + output tokens / TPS
        #

        if tps is not None and float(tps) > 0:

            estimated_latency = (
                float(ttft or 0.0)
                + (
                    float(estimated_output_tokens)
                    / float(tps)
                )
            )

        else:
            # If EcoLogits has no deployment throughput data,
            # fall back to a conservative latency estimate.
            estimated_latency = max(
                1.0,
                float(estimated_output_tokens) / 20.0,
            )

        # ---------------------------------------------------------
        # 5. Split provider and model name
        # ---------------------------------------------------------

        if "/" not in model:
            return cls._fallback(
                estimated_output_tokens
            )

        provider, model_name = model.split(
            "/",
            1,
        )

        # ---------------------------------------------------------
        # 6. Run EcoLogits pre-inference estimation
        # ---------------------------------------------------------

        try:

            impacts = llm_impacts(
                provider=provider,
                model_name=model_name,
                output_token_count=int(
                    estimated_output_tokens
                ),
                request_latency=float(
                    estimated_latency
                ),
            )

        except Exception:

            return cls._fallback(
                estimated_output_tokens
            )

        # ---------------------------------------------------------
        # 7. Check EcoLogits result
        # ---------------------------------------------------------

        if getattr(
            impacts,
            "has_errors",
            False,
        ):

            return cls._fallback(
                estimated_output_tokens
            )

        # ---------------------------------------------------------
        # 8. Extract energy and carbon
        # ---------------------------------------------------------

        try:

            energy_kwh = cls._numeric_value(
                impacts.energy.value
            )

            carbon_kg = cls._numeric_value(
                impacts.gwp.value
            )

        except Exception:

            return cls._fallback(
                estimated_output_tokens
            )

        energy_wh = energy_kwh * 1000.0
        carbon_g = carbon_kg * 1000.0

        # ---------------------------------------------------------
        # 9. GreenLens green score
        # ---------------------------------------------------------

        green_score = 10.0 / (
            1.0 + energy_wh
        )

        green_score = max(
            0.0,
            min(
                10.0,
                green_score,
            ),
        )

        return PreInferenceSustainabilityResult(
            energy_wh=round(
                energy_wh,
                4,
            ),
            carbon_g=round(
                carbon_g,
                4,
            ),
            green_score=round(
                green_score,
                2,
            ),
            source="ecologits_pre_inference",
            available=True,
        )

    @staticmethod
    def _numeric_value(value) -> float:
        """
        Convert an EcoLogits scalar or RangeValue into
        a representative numeric value.

        For a RangeValue, use its midpoint.
        """

        if (
            hasattr(value, "min")
            and hasattr(value, "max")
        ):

            return (
                float(value.min)
                + float(value.max)
            ) / 2.0

        return float(value)

    @staticmethod
    def _fallback(
        estimated_output_tokens: int,
    ) -> PreInferenceSustainabilityResult:

        fallback = CarbonEngine.estimate(
            total_tokens=estimated_output_tokens
        )

        return PreInferenceSustainabilityResult(
            energy_wh=fallback.energy_wh,
            carbon_g=fallback.carbon_g,
            green_score=fallback.green_score,
            source="carbon_engine_fallback",
            available=False,
        )