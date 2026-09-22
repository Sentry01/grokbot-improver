# Grok×Jev Continuous Improvement Loop

## Flow
1. **Log** — Grok Bot appends one JSON line per gate decision to `logs/decisions.jsonl`
2. **Review** (scheduled) — Chief of Staff runs the improvement skill: score false skips / false holds / good catches
3. **Propose** — threshold or question-map tweaks written to `proposals/`
4. **Apply or hold** — safe threshold nudges (±0.05) auto-apply with note; larger changes need user OK
5. **Regress** — re-run trap suite (`../demo` patterns) into `baselines/`
6. **Report** — weekday digest to the user only when something changed or a regression failed

## Decision log schema (one JSON object per line)
```json
{
  "ts": "ISO-8601",
  "agent": "Grok Bot",
  "gate": "tool-worth-it",
  "action": "skip_tool",
  "proceed": false,
  "scores": {},
  "state_summary": "short free text",
  "counterfactual": "what would have happened ungated",
  "outcome_later": null
}
```
Optional `outcome_later`: `good_skip` | `bad_skip` | `good_hold` | `bad_hold` | `good_allow` | `bad_allow` when known.
