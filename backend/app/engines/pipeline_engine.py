"""
GreenLens Level-1 Pipeline

Connects the eight stages of the GreenLens pipeline.
"""

from app.engines.capability_engine import CapabilityEngine
from app.engines.carbon_engine import CarbonEngine
from app.engines.complexity_engine import ComplexityEngine
from app.engines.explanation_engine import ExplanationEngine
from app.engines.model_selection_engine import ModelSelectionEngine
from app.engines.optimizer_engine import OptimizerEngine
from app.engines.task_embedding_engine import TaskEmbeddingEngine


class PipelineEngine:
    """
    Orchestrates the complete Level-1 GreenLens pipeline.
    """

    def __init__(self):
        self.embedding_engine = TaskEmbeddingEngine()

    def run(
        self,
        prompt: str,
        models: list[dict],
    ) -> dict:
        """
        Run all eight pipeline stages.
        """

        # Stage 1: Task Input
        task_input = prompt

        # Stage 2: Task Embedding
        embedding = self.embedding_engine.generate_embedding(
            task_input
        )

        # Stage 3: Complexity Estimation
        complexity = ComplexityEngine.estimate(
            task_input
        )

        # Determine task type
        task_type = self._determine_task_type(
            task_input
        )

        candidates = []

        for model in models:
            model_id = model["model"]

            # Stage 4: Capability Prediction
            capability = CapabilityEngine.predict(
                model=model_id,
                task_type=task_type,
                model_metadata=model,
            )

            # Use the verified LiveBench score when
            # available.
            #
            # If no verified capability data exists,
            # use a neutral fallback for the Level-1
            # prototype so the optimization stage
            # can continue without pretending that
            # the score came from LiveBench.
            capability_score = (
                capability.score
                if capability.available
                else 5.0
            )

            # Stage 5: Carbon Prediction
            carbon = CarbonEngine.estimate(
                total_tokens=model.get(
                    "estimated_tokens",
                    500,
                )
            )

            # Level-1 latency estimate
            latency_score = model.get(
                "latency_score",
                5.0,
            )

            # Stage 6: Constraint Optimization
            optimization = OptimizerEngine.optimize(
                model=model_id,
                capability_score=capability_score,
                carbon_score=carbon.green_score,
                latency_score=latency_score,
                complexity_score=complexity.score,
            )

            candidates.append(
                {
                    "model": model_id,
                    "score": optimization.score,
                    "capability_score": capability_score,
                    "capability_source": capability.source,
                    "capability_available": capability.available,
                    "carbon_score": carbon.green_score,
                    "latency_score": latency_score,
                    "complexity_score": complexity.score,
                    "energy_wh": carbon.energy_wh,
                    "carbon_g": carbon.carbon_g,
                }
            )

        # Stage 7: Model Selection
        selection = ModelSelectionEngine.select_from_candidates(
            candidates
        )

        # Stage 8: Explanation
        explanation = ExplanationEngine.explain(
            selected_model=selection["selected_model"],
            candidates=candidates,
        )

        return {
            "task": {
                "prompt": task_input,
                "task_type": task_type,
                "complexity": complexity.to_dict(),
                "embedding_dimensions": len(embedding),
            },
            "selection": selection,
            "explanation": explanation.to_dict(),
        }

    @staticmethod
    def _determine_task_type(prompt: str) -> str:
        """
        Determine the task category for Level 1.
        """

        text = prompt.lower()

        coding_keywords = {
            "code",
            "python",
            "program",
            "debug",
            "function",
            "class",
            "api",
            "algorithm",
        }

        reasoning_keywords = {
            "solve",
            "calculate",
            "derive",
            "prove",
            "reason",
            "analyze",
        }

        writing_keywords = {
            "write",
            "essay",
            "article",
            "summarize",
            "rewrite",
        }

        if any(
            keyword in text
            for keyword in coding_keywords
        ):
            return "coding"

        if any(
            keyword in text
            for keyword in reasoning_keywords
        ):
            return "reasoning"

        if any(
            keyword in text
            for keyword in writing_keywords
        ):
            return "writing"

        return "general"