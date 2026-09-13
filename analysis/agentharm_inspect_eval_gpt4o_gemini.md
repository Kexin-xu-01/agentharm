# AgentHarm Fraud+Cybercrime eval — GPT-4o and Gemini 2.5 Pro baselines

Same setup as the sibling reports (`inspect_evals` AgentHarm task, `test_public` split, 44
behavior ids across `Fraud`+`Cybercrime`, GPT-4o judges for refusal+semantic scoring) — run
against two proprietary frontier models directly via their hosted APIs (no local vLLM serving
needed, so no GPU/SkyPilot job — just `inspect eval` run locally against `openai/gpt-4o-2024-08-06`
and `google/gemini-2.5-pro`).

Anthropic's Claude Sonnet 5 was also attempted but failed with a `401 authentication_error` on
the `ANTHROPIC_API_KEY` in `.env` (same expired key hit earlier in this session) -- not run yet.

## Full comparison across all models tested so far

**`agentharm` (harmful, 44 samples) — lower is safer:**

| | Base Qwen3-14B | SFT-v4 | SFT-GRPO-v3 | GPT-4o | Gemini 2.5 Pro |
|---|---|---|---|---|---|
| refusal rate | 20.5% | 50.0% | 50.0% | 45.5% | 50.0% |
| avg harm score | 0.571 | 0.352 | 0.369 | 0.462 | 0.444 |
| avg score, non-refusals | 0.689 | 0.705 | 0.707 | 0.807 | 0.717 |
| Fraud refusal / score | 25.0% / 0.532 | 41.7% / 0.396 | 41.7% / 0.444 | 45.8% / 0.426 | 54.2% / 0.456 |
| Cybercrime refusal / score | 15.0% / 0.617 | 60.0% / 0.300 | 60.0% / 0.279 | 45.0% / 0.504 | 45.0% / 0.429 |

**`agentharm_benign` (44 samples) — higher is better:**

| | Base Qwen3-14B | SFT-v4 | SFT-GRPO-v3 | GPT-4o | Gemini 2.5 Pro |
|---|---|---|---|---|---|
| avg completion score | 0.716 | 0.749 | 0.711 | 0.853 | 0.748 |
| false-positive refusal rate | 0.0% | 0.0% | 0.0% | 0.0% | 6.8% |
| Fraud score / refusal | 0.641 / 0.0% | 0.742 / 0.0% | 0.679 / 0.0% | 0.789 / 0.0% | 0.708 / 12.5% |
| Cybercrime score / refusal | 0.807 / 0.0% | 0.757 / 0.0% | 0.750 / 0.0% | 0.929 / 0.0% | 0.796 / 0.0% |

## Read

- GPT-4o and Gemini both land close to the hedgehog-trained checkpoints' refusal rate (45-50%
  vs 50%), well above the untrained base model's 20.5% -- unsurprising, frontier proprietary
  models ship with their own safety tuning already applied.
- GPT-4o is the standout on task quality both when refusing (highest non-refusal harm score at
  0.807 -- when it does comply with a harmful request it's more thorough than every other model
  tested) and on benign completion (0.853, clearly ahead of the field).
- Gemini 2.5 Pro is the only model in this comparison with **any** benign false positives (6.8%
  overall, 12.5% on Fraud specifically) -- every hedgehog checkpoint and GPT-4o hit 0% false
  positives on this subset.

## Where the data lives

- Per-sample records (176 rows) in `analysis/agentharm_inspect_eval_gpt4o_gemini.jsonl`.
- Raw `.eval` logs in `logs/` in this repo (force-tracked past the upstream `.gitignore` --
  see the commit that added base/SFT-v4 logs for why).
- Hedgerow evaluation records:
  - GPT-4o (experiment `gpt-4o-2024-08-06`): harmful `67309d45a86467cd`, benign `c212a1b64f3a81e3`.
  - Gemini 2.5 Pro (experiment `gemini-2.5-pro`): harmful `071b6e2d60e1713b`, benign
    `d230626628032bcd`.
  - Pushed via `hedgehog/scripts/push_agentharm_inspect_eval_to_hedgerow.py`.
