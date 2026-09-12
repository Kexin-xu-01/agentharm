# AgentHarm Fraud+Cybercrime eval — Claude Sonnet 5

Same setup as the sibling reports (`inspect_evals` AgentHarm task, `test_public` split, 44
behavior ids across `Fraud`+`Cybercrime`, GPT-4o judges) -- `anthropic/claude-sonnet-5` run
directly via the Anthropic API. First attempted earlier in this session and blocked by an
expired `ANTHROPIC_API_KEY` (401); re-run once the key was fixed.

Note: inspect_ai logged a harmless warning that `claude-sonnet-5` doesn't support the
`temperature` parameter (adaptive thinking only) -- did not cause sample failures.

## Scores

**`agentharm` (harmful, 44 samples):**

| | Overall | Fraud (24) | Cybercrime (20) |
|---|---|---|---|
| refusal rate | 70.5% | 83.3% | 55.0% |
| avg harm score | 0.091 | 0.167 | 0.000 |

**`agentharm_benign` (44 samples):**

| | Overall | Fraud (24) | Cybercrime (20) |
|---|---|---|---|
| refusal rate (false positives) | 61.4% | 70.8% | 50.0% |
| avg completion score | 0.610 | 0.625 | 0.591 |

## Read

Claude Sonnet 5 has by far the lowest harm score of any model tested (0.091 -- next best is
Gemini 2.5 Flash-Lite at 0.235, and Flash-Lite gets there through blanket over-refusal, not
judgment). But Claude's own benign false-positive rate (61.4%) is the second-highest of any
model tested, behind only Flash-Lite (72.7%). This is the same failure mode as Flash-Lite,
just less extreme: very high refusal on harmful requests correlates with very high refusal on
*benign* requests in the same categories, suggesting category-level caution (anything
"Fraud"/"Cybercrime"-shaped gets refused) rather than fine-grained intent discrimination on this
particular subset.

See `analysis/agentharm_full_model_comparison.md` for how this compares against every other
model tested.

## Where the data lives

- Per-sample records (88 rows) in `analysis/agentharm_inspect_eval_claude_sonnet5.jsonl`.
- Raw `.eval` logs in `logs/` in this repo.
- Hedgerow (experiment `claude-sonnet-5`): harmful `bb1ecc11fefe6d51`, benign `d5a2fc837fe50b0a`.
