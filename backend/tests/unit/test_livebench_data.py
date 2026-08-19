from pathlib import Path

from app.integrations.livebench_data import (
    LiveBenchDataLoader,
)


def test_livebench_data_loader(tmp_path: Path):

    csv_file = tmp_path / "livebench.csv"

    csv_file.write_text(
        "model,overall,reasoning,coding,agentic_coding,"
        "mathematics,data_analysis,language,"
        "instruction_following\n"
        "test-model,80.0,78.0,85.0,80.0,"
        "78.0,79.0,81.0,83.0\n",
        encoding="utf-8",
    )

    loader = LiveBenchDataLoader(
        str(csv_file)
    )

    results = loader.load()

    assert "test-model" in results
    assert results["test-model"]["overall"] == 80.0
    assert results["test-model"]["coding"] == 85.0
    assert results["test-model"]["reasoning"] == 78.0