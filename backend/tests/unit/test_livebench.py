from app.integrations.livebench import (
    LiveBenchIntegration,
    LiveBenchScore,
)


MODEL = "openai/gpt-oss-20b:free"


def test_add_and_get_score():

    score = LiveBenchScore(
        model=MODEL,
        overall_score=80.0,
        reasoning_score=82.0,
        coding_score=85.0,
        agentic_coding_score=80.0,
        mathematics_score=78.0,
        data_analysis_score=79.0,
        language_score=81.0,
        instruction_following_score=83.0,
    )

    LiveBenchIntegration.load_scores(
        {
            MODEL: {
                "overall": score.overall_score,
                "reasoning": score.reasoning_score,
                "coding": score.coding_score,
                "agentic_coding": score.agentic_coding_score,
                "mathematics": score.mathematics_score,
                "data_analysis": score.data_analysis_score,
                "language": score.language_score,
                "instruction_following": (
                    score.instruction_following_score
                ),
            }
        }
    )

    result = LiveBenchIntegration.get_score(MODEL)

    assert result is not None
    assert result.model == MODEL
    assert result.coding_score == 85.0


def test_unknown_model():

    result = LiveBenchIntegration.get_score(
        "unknown-model"
    )

    assert result is None