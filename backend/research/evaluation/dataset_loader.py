"""Load a frozen existing GreenLens evaluation prompt dataset."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

REQUIRED = {"prompt_id", "task_type", "prompt"}


def load_dataset(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {source}. Export and freeze the existing GreenLens evaluation prompts first; "
            "LiveBench capability profiles are not a substitute for executable prompts."
        )
    data = json.loads(source.read_text(encoding="utf-8"))
    prompts = data.get("prompts") if isinstance(data, dict) else None
    if not isinstance(prompts, list) or not prompts:
        raise ValueError("Dataset must contain a non-empty 'prompts' array")
    seen: set[str] = set()
    for index, item in enumerate(prompts):
        if not isinstance(item, dict) or not REQUIRED.issubset(item):
            raise ValueError(f"Prompt at index {index} must contain {sorted(REQUIRED)}")
        prompt_id = str(item["prompt_id"]).strip()
        if not prompt_id or prompt_id in seen:
            raise ValueError(f"Missing or duplicate prompt_id at index {index}")
        if not str(item["prompt"]).strip() or not str(item["task_type"]).strip():
            raise ValueError(f"Prompt and task_type must be non-empty for {prompt_id}")
        seen.add(prompt_id)
    return data
