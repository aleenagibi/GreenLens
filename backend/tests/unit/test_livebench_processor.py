import pandas as pd

from app.integrations.livebench_processor import (
    LiveBenchProcessor,
)


def test_category_score_calculation(tmp_path):

    csv_file = tmp_path / "livebench.csv"

    dataframe = pd.DataFrame(
        [
            {
                "model": "test-model",

                "theory_of_mind": 80,
                "zebra_puzzle": 90,
                "spatial": 70,
                "logic_with_navigation": 60,

                "code_generation": 90,
                "code_completion": 80,

                "javascript": 70,
                "typescript": 80,
                "python": 90,

                "AMPS_Hard": 60,
                "integrals_with_game": 70,
                "math_comp": 80,
                "olympiad": 90,

                "consecutive_events": 80,
                "tablejoin": 70,
                "tablereformat": 90,

                "connections": 80,
                "plot_unscrambling": 70,
                "typos": 90,

                "paraphrase": 90,
                "simplify": 80,
                "story_generation": 70,
                "summarize": 60,
            }
        ]
    )

    dataframe.to_csv(
        csv_file,
        index=False,
    )

    processor = LiveBenchProcessor(
        str(csv_file)
    )

    results = processor.calculate_category_scores(
        processor.load()
    )

    result = results[0]

    assert result["model"] == "test-model"

    assert result["reasoning"] == 75.0
    assert result["coding"] == 85.0
    assert result["agentic_coding"] == 80.0
    assert result["mathematics"] == 75.0
    assert result["data_analysis"] == 80.0
    assert result["language"] == 80.0
    assert result["instruction_following"] == 75.0

    assert result["overall"] is not None