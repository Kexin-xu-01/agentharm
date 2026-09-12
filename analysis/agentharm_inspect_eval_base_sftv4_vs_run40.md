# AgentHarm Fraud+Cybercrime eval — base Qwen3-14B vs SFT-v4 vs GRPO run40

Same setup as `agentharm_inspect_eval_run40_fraud_cybercrime.md` (inspect_evals AgentHarm task,
`test_public` split, 44 behavior ids across `Fraud`+`Cybercrime`, model served via `inspect_ai`'s
`vllm/` provider with the `hermes` tool-call-parser fix, GPT-4o refusal+semantic judges) — run
against two more checkpoints for comparison:

- **Base Qwen3-14B**: `Qwen/Qwen3-14B`, untrained, no hedgehog fine-tuning at all.
- **SFT-v4**: `hedgehog-train_42` merged model, Hedgerow experiment `sft-v4` — SFT continued
  from the v1 checkpoint (`hedgehog-train_21`'s adapter) on the `agentharm_sft_toolcalling_v2_v3_v4`
  dataset (2419 rows).
- **GRPO run40**: `hedgehog-train_40` merged model, Hedgerow experiment
  `agentharm-sft-grpo-v2-v3-lmmjudge` — already covered in the sibling report; included here for
  comparison. GRPO run40 warm-started from a *different, earlier* SFT checkpoint
  (`hedgehog-train_39`'s `agentharm-sft-toolcalling-v2-v3` adapter step-500), not from SFT-v4 --
  the two are siblings off the same v1 base, not a continuation of each other.

## Scores

**`agentharm` (harmful, 44 samples) — lower is safer:**

| | Base Qwen3-14B | SFT-v4 | GRPO run40 |
|---|---|---|---|
| refusal rate | 20.5% | 50.0% | 50.0% |
| avg harm score | 0.571 | 0.352 | 0.369 |
| avg score on non-refusals | 0.689 | 0.705 | 0.707 |
| Fraud refusal / score | 25.0% / 0.532 | 41.7% / 0.396 | 41.7% / 0.444 |
| Cybercrime refusal / score | 15.0% / 0.617 | 60.0% / 0.300 | 60.0% / 0.279 |

**`agentharm_benign` (44 samples) — higher is better:**

| | Base Qwen3-14B | SFT-v4 | GRPO run40 |
|---|---|---|---|
| avg completion score | 0.716 | 0.749 | 0.711 |
| false-positive refusal rate | 0.0% | 0.0% | 0.0% |
| Fraud score | 0.641 | 0.742 | 0.679 |
| Cybercrime score | 0.807 | 0.757 | 0.750 |

## Read

- Safety fine-tuning (SFT-v4 and GRPO run40 alike) more than **doubles refusal rate** on harmful
  requests (20.5% -> 50%), and that's where nearly all the harm-score reduction comes from —
  `avg_score_non_refusals` barely moves (0.689 -> ~0.706), meaning training isn't making the
  model meaningfully more cautious/incomplete when it *does* comply, just making it comply less
  often.
- SFT-v4 and GRPO run40 land on almost identical refusal behavior (both 50% overall, 41.7%/60%
  Fraud/Cybercrime split) despite different training lineages (different warm-start SFT
  checkpoint, GRPO run40 additionally has RL on top) — GRPO didn't shift refusal rate further on
  this particular subset, and its harm score is marginally *worse* than SFT-v4 alone on
  Cybercrime (0.279 vs 0.300).
- No false-positive regression on benign tasks for either trained checkpoint versus base — both
  stay at 0% refusal and are in the same 0.71-0.75 completion-score range as base.

## Where the data lives

- Per-sample records (176 rows: 44 x 4 run/task combos) in
  `analysis/agentharm_inspect_eval_base_sftv4_vs_run40.jsonl` in this repo.
- Raw `.eval` logs:
  `gs://alwaysfurther-training-workspace/shared/kexin/agentharm-inspect-eval/base-untrained-qwen3-14b/...`
  and `.../sft-v4/...` (same bucket layout as the run40 report).
- Hedgerow evaluation records:
  - Base Qwen3-14B (experiment `base-untrained-qwen3-14b`): harmful `14b89b8a07d8a89b`, benign
    `098a722d9527b6a3`.
  - SFT-v4 (experiment `sft-v4`): harmful `58ec08855e9b3944`, benign `c5d1e4a22b4c35af`.
  - GRPO run40: see sibling report (`56f4acbf2c2a2164`, `14c45c301c989504`).
  - Pushed via `hedgehog/scripts/push_agentharm_inspect_eval_to_hedgerow.py` (same schema-mapping
    tool used for run40 — see that script's docstring for the Hedgerow schema gotcha).
