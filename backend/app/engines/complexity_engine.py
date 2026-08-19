"""
Complexity Engine

Estimates the complexity of a user task using
simple, explainable prompt features.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ComplexityResult:
    level: str
    score: float
    factors: list[str]

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "score": self.score,
            "factors": self.factors,
        }


class ComplexityEngine:
    """
    Estimates task complexity using rule-based features.
    """

    COMPLEXITY_KEYWORDS = {
        "analyze",
        "compare",
        "design",
        "develop",
        "implement",
        "optimize",
        "debug",
        "derive",
        "prove",
        "architecture",
        "algorithm",
        "research",
        "evaluate",
    }

    CODE_KEYWORDS = {
        "code",
        "program",
        "python",
        "java",
        "javascript",
        "function",
        "class",
        "api",
        "algorithm",
        "debug",
        "implement",
    }

    @classmethod
    def estimate(cls, prompt: str) -> ComplexityResult:
        """
        Estimate the complexity of a prompt.
        """

        text = prompt.lower()
        words = text.split()

        score = 1.0
        factors: list[str] = []

        keyword_matches = sum(
            keyword in text
            for keyword in cls.COMPLEXITY_KEYWORDS
        )

        if keyword_matches >= 3:
            score += 3.0
            factors.append(
                "Multiple complex task requirements"
            )
        elif keyword_matches >= 1:
            score += 1.5
            factors.append(
                "Complex task requirement detected"
            )

        if len(words) > 100:
            score += 2.0
            factors.append("Long prompt")
        elif len(words) > 50:
            score += 1.0
            factors.append("Moderately long prompt")

        code_matches = sum(
            keyword in text
            for keyword in cls.CODE_KEYWORDS
        )

        if code_matches >= 2:
            score += 1.5
            factors.append(
                "Programming or implementation requirements"
            )

        if "step by step" in text:
            score += 1.0
            factors.append(
                "Step-by-step reasoning requested"
            )

        score = min(score, 10.0)

        if score >= 7:
            level = "high"
        elif score >= 4:
            level = "medium"
        else:
            level = "low"

        if not factors:
            factors.append(
                "Simple informational request"
            )

        return ComplexityResult(
            level=level,
            score=round(score, 2),
            factors=factors,
        )