# Qwen3-14B SFT-GRPO-v3 (experiment `agentharm-sft-grpo-v2-v3-lmmjudge`) — inspect_evals AgentHarm eval, Fraud+Cybercrime subset

Job: `sky-managed-2026-09-05-15-36-00-324097_hedgehog-train_40-0`, merged model at
`/workspace/shared/outputs/jupyterhub-hub@gen-lang-client-0808823325.iam.gserviceaccount.com/sky-managed-2026-09-05-15-36-00-324097_hedgehog-train_40-0/merged`
(base `Qwen/Qwen3-14B`, GRPO 495 steps, warm-started from the `agentharm-sft-toolcalling-v2-v3`
SFT checkpoint's step-500 early-stop adapter, llm-judge/GPT-4o refusal detector).

This is the first model benchmarked in this repo, via the upstream `inspect_evals` AgentHarm
task (`ai-safety-institute/AgentHarm` public dataset, `test_public` split) run with `inspect
eval` and the model served locally through `inspect_ai`'s `vllm/` provider -- not hedgehog's own
`evaluate` harness (which already ran post-train via `RUN_EVAL=1` and logged to Hedgerow under
this same experiment separately). Filtered to the 44 behavior ids in the `Fraud` and
`Cybercrime` categories (24 + 20), both the harmful (`agentharm`) and benign
(`agentharm_benign`) variants -- 88 samples total.

## How it was run

- SkyPilot job definition: `hedgehog/scripts/agentharm-inspect-eval.sky.yaml` -- installs
  `inspect_ai`/`inspect-evals`/`vllm` into a `uv` Python-3.12 venv, since the default GCP image's
  system Python was too old for `inspect-evals==0.20.0`.
- Model served via `--model vllm/<merged-path>` (inspect_ai starts/manages the vLLM OpenAI-
  compatible server itself). Required `VLLM_DEFAULT_SERVER_ARGS` with
  `enable_auto_tool_choice: true`, `tool_call_parser: hermes`, and an explicit `chat_template`
  pointing at the model's own `chat_template.jinja` -- without these, vLLM 400s on any
  `tool_choice="auto"` request (AgentHarm's default agent always sends `auto`); the model's
  chat template uses the standard `<tool_call>{"name":...,"arguments":...}</tool_call>` tag
  format, which the `hermes` parser matches.
- Judges: `openai/gpt-4o-2024-08-06` for both refusal and semantic (task-completion) grading
  (inspect_evals `agentharm` task defaults).
- Three sky job attempts before a clean run: one failed setup (python version), one ran but
  every sample failed on the vLLM tool-choice 400 above, the third succeeded with the fix.

## Scores

**`agentharm` (harmful, 44 samples)** -- safety behavior, higher refusal / lower score is safer:

| | Overall | Fraud (24) | Cybercrime (20) |
|---|---|---|---|
| refusal rate | 50.0% | 41.7% | 60.0% |
| avg harm score (checklist completion fraction) | 0.369 | 0.444 | 0.279 |
| avg score on non-refusals only | 0.707 | -- | -- |

**`agentharm_benign` (44 samples)** -- task-completion behavior, higher is better, refusals here are false positives:

| | Overall | Fraud (24) | Cybercrime (20) |
|---|---|---|---|
| refusal rate (false positives) | 0.0% | 0.0% | 0.0% |
| avg completion score | 0.711 | 0.679 | 0.750 |

See `analysis/agentharm_full_model_comparison.md` for how this compares against every other
model tested.

## Where the data lives

- Full per-sample records (prompt, response preview, category, score, refusal, explanation)
  for all 88 samples: `agentharm_inspect_eval_run40_fraud_cybercrime.jsonl` in this directory.
- Raw `.eval` log files (complete transcripts, tool calls, judge outputs): `logs/` in this repo.
- Hedgerow (https://hedgerow.nolabs.dev, experiment `agentharm-sft-grpo-v2-v3-lmmjudge`):
  `56f4acbf2c2a2164` (harmful), `14c45c301c989504` (benign). Metrics remapped into Hedgerow's
  fixed `SecurityMetrics`/`EvaluationResult` schema (which doesn't natively have "checklist
  completion fraction" as a concept) -- `attacks_refused`/`attacks_succeeded`/`by_attack_type`
  for the harmful eval, `benign_completed` defined as achieving a **full** (1.0) checklist score
  (stricter than this report's partial-credit `avg_score`); each per-sample row's `reward` field
  carries the raw 0-1 completion fraction, and `completed_task` is the same full-score
  threshold.

## Reproducing / extending

```bash
sky jobs launch scripts/agentharm-inspect-eval.sky.yaml -n agentharm-inspect-<tag> -y \
  --env MODEL_PATH=/workspace/shared/outputs/<you>/<task-id>/merged \
  --env BEHAVIOR_IDS="['13-1','13-2',...]" \
  --env SOURCE_EXPERIMENT=<hedgerow-experiment-tag> \
  --env OPENAI_API_KEY --env LAUNCHED_BY=$(gcloud config get-value account)
```

Behavior ids for other categories: pull from the public dataset directly, e.g.

```python
from datasets import load_dataset
ds = load_dataset("ai-safety-institute/AgentHarm", "harmful", split="test_public")
ids = sorted(r["id"] for r in ds if r["category"] == "<CategoryName>")
```
