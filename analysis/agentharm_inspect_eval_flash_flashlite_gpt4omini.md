# AgentHarm Fraud+Cybercrime eval — Gemini 2.5 Flash/Flash-Lite and GPT-4o-mini

Same setup as the sibling reports (`inspect_evals` AgentHarm task, `test_public` split, 44
behavior ids across `Fraud`+`Cybercrime`, GPT-4o judges) -- three more proprietary "smaller/
cheaper tier" models, run directly via hosted APIs (no GPU needed).

## Full comparison across every model tested so far

**`agentharm` (harmful, 44 samples) — lower is safer:**

| | Base Qwen3-14B | SFT-v4 | GRPO run40 | GPT-4o | GPT-4o-mini | Gemini 2.5 Pro | Gemini 2.5 Flash | Gemini 2.5 Flash-Lite |
|---|---|---|---|---|---|---|---|---|
| refusal rate | 20.5% | 50.0% | 50.0% | 45.5% | 25.0% | 50.0% | 59.1% | 86.4% |
| avg harm score | 0.571 | 0.352 | 0.369 | 0.462 | 0.523 | 0.444 | 0.334 | 0.235 |
| avg score, non-refusals | 0.689 | 0.705 | 0.707 | 0.807 | 0.631 | 0.717 | 0.802 | 0.000* |
| Fraud refusal / score | 25.0%/0.532 | 41.7%/0.396 | 41.7%/0.444 | 45.8%/0.426 | 20.8%/0.491 | 54.2%/0.456 | 62.5%/0.375 | 100%/0.278 |
| Cybercrime refusal / score | 15.0%/0.617 | 60.0%/0.300 | 60.0%/0.279 | 45.0%/0.504 | 30.0%/0.561 | 45.0%/0.429 | 55.0%/0.286 | 70.0%/0.183 |

\* Flash-Lite refused essentially every Fraud sample (100%) and most Cybercrime (70%); the tiny
non-refusal remainder scored ~0, not a meaningful "quality when complying" signal at that sample
size.

**`agentharm_benign` (44 samples) — higher is better:**

| | Base Qwen3-14B | SFT-v4 | GRPO run40 | GPT-4o | GPT-4o-mini | Gemini 2.5 Pro | Gemini 2.5 Flash | Gemini 2.5 Flash-Lite |
|---|---|---|---|---|---|---|---|---|
| avg completion score | 0.716 | 0.749 | 0.711 | 0.853 | 0.762 | 0.748 | 0.774 | 0.454 |
| false-positive refusal rate | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 6.8% | 0.0% | **72.7%** |
| Fraud score / refusal | 0.641/0% | 0.742/0% | 0.679/0% | 0.789/0% | 0.649/0% | 0.708/12.5% | 0.749/0% | 0.488/83.3% |
| Cybercrime score / refusal | 0.807/0% | 0.757/0% | 0.750/0% | 0.929/0% | 0.897/0% | 0.796/0% | 0.804/0% | 0.414/60.0% |

## Read

- Clear **tier effect within each family**: the larger/flagship variant refuses less and scores
  higher on both harmful-compliance-quality and benign completion than its smaller sibling --
  GPT-4o vs GPT-4o-mini (45.5% vs 25.0% harmful refusal; 0.853 vs 0.762 benign) is the one
  exception in the *opposite* direction of what you'd expect from "smaller = less safety-tuned";
  GPT-4o-mini actually refuses harmful requests *less* than GPT-4o.
- The Gemini family shows the opposite, sharper pattern: refusal rate climbs steeply as the
  model gets smaller/cheaper (Pro 50.0% -> Flash 59.1% -> Flash-Lite 86.4%), and benign
  completion quality collapses in lockstep (0.748 -> 0.774 -> 0.454). This isn't "safer" in a
  useful sense -- it's **indiscriminate over-refusal**.
- **Gemini 2.5 Flash-Lite is a severe outlier**: 72.7% false-positive refusal rate on strictly
  benign Fraud/Cybercrime-adjacent tasks (83.3% on Fraud specifically) -- nothing else tested
  clears 7%. It also has the lowest harmful-avg-score (0.235, "safest" by that one number) but
  that's driven entirely by blanket refusal, not by better judgment: it refuses 100% of harmful
  Fraud requests AND 83% of *benign* Fraud requests, i.e. it can't distinguish the two on this
  subset.

## Where the data lives

- Per-sample records (264 rows) in
  `analysis/agentharm_inspect_eval_flash_flashlite_gpt4omini.jsonl`.
- Raw `.eval` logs in `logs/` in this repo.
- Hedgerow evaluation records:
  - Gemini 2.5 Flash (experiment `gemini-2.5-flash`): harmful `81d181dd7498bba9`, benign
    `a33ffcf9ebaeaebf`.
  - Gemini 2.5 Flash-Lite (experiment `gemini-2.5-flash-lite`): harmful `cf99d55ab365db52`,
    benign `8ed18e08aa77b6ca`.
  - GPT-4o-mini (experiment `gpt-4o-mini`): harmful `a59a07b71bde2812`, benign `fcffc49ea4b818bd`.
  - Pushed via `hedgehog/scripts/push_agentharm_inspect_eval_to_hedgerow.py`.
