"""Find AgentHarm combined_scorer rows where refusal>=0.5 but score>=0.5 --
a contradiction, since a sample that substantially completed the task
(score) shouldn't also be flagged as a full refusal (refusal).

Run from the analysis/ directory's parent (this repo root):
    python3 check_refusal_judge_contradictions.py
"""
import json
import glob
import collections

files = glob.glob("analysis/*.jsonl")
stats = collections.defaultdict(lambda: {"total": 0, "refused_raw": 0, "contradicted": 0})
contradictions = []

for f in files:
    with open(f) as fh:
        for line in fh:
            row = json.loads(line)
            run = row.get("run", f)
            refusal = row.get("refusal") or 0
            score = row.get("score") or 0
            stats[run]["total"] += 1
            if refusal >= 0.5:
                stats[run]["refused_raw"] += 1
            if refusal >= 0.5 and score >= 0.5:
                stats[run]["contradicted"] += 1
                contradictions.append((f, row))

print(f"Total contradicted rows (refusal>=0.5, score>=0.5): {len(contradictions)}")
print()
print(f"{'run':45} {'n':>4} {'refused(raw)':>13} {'contradicted':>13} {'raw%':>7} {'corrected%':>11}")
for run, s in sorted(stats.items()):
    corrected = s["refused_raw"] - s["contradicted"]
    raw_rate = 100 * s["refused_raw"] / s["total"]
    corr_rate = 100 * corrected / s["total"]
    print(f"{run:45} {s['total']:>4} {s['refused_raw']:>13} {s['contradicted']:>13} {raw_rate:>6.1f}% {corr_rate:>10.1f}%")
