"""
LiveBench Data Loader

Loads a verified LiveBench leaderboard snapshot.
"""

import csv
from pathlib import Path


class LiveBenchDataLoader:
    """
    Loads LiveBench leaderboard data from CSV.
    """

    REQUIRED_COLUMNS = {
        "model",
        "overall",
        "reasoning",
        "coding",
        "agentic_coding",
        "mathematics",
        "data_analysis",
        "language",
        "instruction_following",
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> dict[str, dict[str, float]]:
        """
        Load and validate LiveBench scores.
        """

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"LiveBench data not found: {self.file_path}"
            )

        with self.file_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError(
                    "LiveBench CSV has no header."
                )

            missing = (
                self.REQUIRED_COLUMNS
                - set(reader.fieldnames)
            )

            if missing:
                raise ValueError(
                    "Missing LiveBench columns: "
                    + ", ".join(sorted(missing))
                )

            results = {}

            for row in reader:
                model = row["model"].strip()

                if not model:
                    continue

                results[model] = {
                    "overall": float(row["overall"]),
                    "reasoning": float(row["reasoning"]),
                    "coding": float(row["coding"]),
                    "agentic_coding": float(
                        row["agentic_coding"]
                    ),
                    "mathematics": float(
                        row["mathematics"]
                    ),
                    "data_analysis": float(
                        row["data_analysis"]
                    ),
                    "language": float(
                        row["language"]
                    ),
                    "instruction_following": float(
                        row["instruction_following"]
                    ),
                }

            return results