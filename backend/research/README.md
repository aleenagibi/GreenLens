# GreenLens local research evaluation (CHR)

This package is research-only. It is intentionally not imported by `app/`, is not registered as a provider/model, and is not connected to production chat or Insights routes.

## Current implementation status

- CHR deterministic selector: implemented.
- Frozen dataset validation: implemented.
- Attempt metric aggregation: implemented.
- Existing executable evaluation prompt dataset: **not found in the uploaded source archive**. The LiveBench files in `app/integrations/` are capability/benchmark evidence and must not be treated as prompt records.
- Provider execution adapter, manual-review workflow, experiment persistence, comparison report and radar export: not implemented in this initial patch. Do not treat the scaffold as a completed experiment runner.

## CHR selection

Input candidates must already have passed the same capability eligibility checks used by GreenLens. Historical calibration is frozen before evaluation. Models below the configured minimum sample count are excluded. The score is `0.50 * capability_fit + 0.30 * historical_reliability + 0.20 * inverse_latency_performance`. Carbon and energy are not read by the selector. Ties use a stable model-ID ordering.

Calibration values must be on a 0–100 scale for success rate and capability fit. Latency is normalised against the eligible pool in the frozen calibration snapshot. The weights and minimum sample threshold must be recorded in the experiment manifest.

## Dataset format

Place a frozen JSON file at `data/research/datasets/greenlens-existing-eval-v1.json` with a top-level `dataset_id` and a non-empty `prompts` array. Each prompt needs `prompt_id`, `task_type`, and `prompt`. Preserve the original existing prompt wording; do not fabricate missing prompts.

## Safety boundary

Run research tools manually in a local development environment only. Never import these modules into `app/`, expose them through the deployed API, add CHR to the production model catalogue, or write their records into `InferenceRecord` / live Insights.
