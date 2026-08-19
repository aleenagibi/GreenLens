"""
LiveBench Processor

Processes the official LiveBench 2026-06-25
model-level benchmark table into category scores.
"""

from pathlib import Path

import pandas as pd


LIVEBENCH_CATEGORY_MAP = {
    "reasoning": [
        "theory_of_mind",
        "zebra_puzzle",
        "spatial",
        "logic_with_navigation",
    ],
    "coding": [
        "code_generation",
        "code_completion",
    ],
    "agentic_coding": [
        "javascript",
        "typescript",
        "python",
    ],
    "mathematics": [
        "AMPS_Hard",
        "integrals_with_game",
        "math_comp",
        "olympiad",
    ],
    "data_analysis": [
        "consecutive_events",
        "tablejoin",
        "tablereformat",
    ],
    "language": [
        "connections",
        "plot_unscrambling",
        "typos",
    ],
    "instruction_following": [
        "paraphrase",
        "simplify",
        "story_generation",
        "summarize",
    ],
}


class LiveBenchProcessor:

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)

    def load(self) -> pd.DataFrame:
        """Load the official LiveBench table."""

        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"LiveBench CSV not found: {self.csv_path}"
            )

        return pd.read_csv(self.csv_path)

    def validate_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """Ensure all required LiveBench columns exist."""

        required = {"model"}

        for tasks in LIVEBENCH_CATEGORY_MAP.values():
            required.update(tasks)

        missing = required - set(dataframe.columns)

        if missing:
            raise ValueError(
                "Missing LiveBench columns: "
                + ", ".join(sorted(missing))
            )

    def calculate_category_scores(
        self,
        dataframe: pd.DataFrame,
    ) -> list[dict]:

        self.validate_columns(dataframe)

        results = []

        for _, row in dataframe.iterrows():

            model = row["model"]

            profile = {
                "model": model,
                "source": "LiveBench",
                "release": "2026-06-25",
            }

            for category, tasks in (
                LIVEBENCH_CATEGORY_MAP.items()
            ):
                scores = [
                    row[task]
                    for task in tasks
                    if pd.notna(row[task])
                ]

                if scores:
                    profile[category] = round(
                        sum(scores) / len(scores),
                        2,
                    )
                else:
                    profile[category] = None

            available_scores = [
                profile[category]
                for category in LIVEBENCH_CATEGORY_MAP
                if profile[category] is not None
            ]

            profile["overall"] = (
                round(
                    sum(available_scores)
                    / len(available_scores),
                    2,
                )
                if available_scores
                else None
            )

            results.append(profile)

        return results