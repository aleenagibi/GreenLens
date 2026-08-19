"""
Generate GreenLens capability data from the
official LiveBench 2026-06-25 release.
"""

import json
from pathlib import Path

from app.integrations.livebench_processor import (
    LiveBenchProcessor,
)


BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = (
    BASE_DIR
    / "data"
    / "benchmarks"
    / "livebench"
    / "table_2026_06_25.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "benchmarks"
    / "livebench"
    / "capability_profiles.json"
)


def main():

    print("Loading LiveBench data...")

    processor = LiveBenchProcessor(
        str(CSV_PATH)
    )

    dataframe = processor.load()

    print(
        f"Found {len(dataframe)} models."
    )

    profiles = processor.calculate_category_scores(
        dataframe
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            profiles,
            file,
            indent=4,
        )

    print(
        f"Generated {len(profiles)} capability profiles."
    )

    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()