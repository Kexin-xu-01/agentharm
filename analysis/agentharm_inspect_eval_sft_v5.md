# AgentHarm Fraud+Cybercrime eval — Qwen3-14B SFT-v5

Same setup as the sibling reports (`inspect_evals` AgentHarm task, `test_public` split, 44
behavior ids across `Fraud`+`Cybercrime`, GPT-4o judges) -- `hedgehog-train_56`, Hedgerow
experiment `sft-v5`, completed 2026-09-13.

Unlike every other hedgehog checkpoint evaluated so far, this run had **no merged model** --
only a LoRA adapter (`lora/`) on top of base `Qwen/Qwen3-14B`. Rather than run a separate merge
job, it was served directly via `inspect_ai`'s `vllm/` provider's native LoRA syntax:
`--model vllm/Qwen/Qwen3-14B:/workspace/.../lora` (base model, colon, local adapter path) --
`vllm` auto-detects the adapter and enables LoRA serving; `CHAT_TEMPLATE` was left empty so
vLLM pulls the chat template from the base `Qwen/Qwen3-14B` HF repo directly (same as the
untrained base-model run) rather than needing an explicit override.

## Scores

**`agentharm` (harmful, 44 samples):**

| | Overall | Fraud (24) | Cybercrime (20) |
|---|---|---|---|
| refusal rate | 61.4% | 54.2% | 70.0% |
| avg harm score | 0.274 | 0.329 | 0.207 |
| avg score on non-refusals only | 0.669 | -- | -- |

**`agentharm_benign` (44 samples):**

| | Overall | Fraud (24) | Cybercrime (20) |
|---|---|---|---|
| refusal rate (false positives) | 2.3% | 4.2% | 0.0% |
| avg completion score | 0.720 | 0.677 | 0.771 |

## Read

SFT-v5 improves on SFT-v4 on both safety axes at once: higher harmful-refusal rate (61.4% vs
50.0%) and a lower harm score (0.274 vs 0.352), while benign completion stays in the same range
(0.720 vs 0.749) -- the only regression is a small false-positive rate (2.3%, one Fraud sample)
where SFT-v4 was a clean 0%. See `analysis/agentharm_full_model_comparison.md` for the full
cross-model comparison.

## Where the data lives

- Per-sample records (88 rows) in `analysis/agentharm_inspect_eval_sft_v5.jsonl`.
- Raw `.eval` logs in `logs/` in this repo.
- Hedgerow (experiment `sft-v5`): harmful `2d567f6549b20604`, benign `efcf48be50fad022`.
