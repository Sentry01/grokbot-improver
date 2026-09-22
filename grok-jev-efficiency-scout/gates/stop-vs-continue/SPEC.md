# Gate: stop-vs-continue

**Name:** Stop-vs-Continue Loop Gate  
**Slug:** `stop-vs-continue`  
**Rank / source:** #4 in `cool-use-cases.md`  
**Primary lever:** cost / latency

## Purpose

End “one more fetch” loops when marginal value of the next tool call is low. Force the harness to produce the user-facing answer.

## When to call

After each tool-result batch / at the loop head before proposing another tool.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `goal` | string | Loop goal |
| `calls_so_far` | string[] | Tools already run |
| `gaps` | string[] | Remaining blockers |
| `budget_pressure` | string | e.g. `prefer finish` |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `should_stop` | `noul` | Stop tool use and answer now |
| `marginal_value_of_next_call` | `score` | negative / near zero / small / material |

No free-text questions.

## Thresholds

- **Stop** if `should_stop.noul >= 0.6` **OR** `marginal_value_of_next_call.score < 1.5`
- Else **continue**

## Fail mode

**Fail-open** → `continue` once on API error (do not strand the loop mid-task; one more iteration allowed).

## Expected efficiency win

Cost + latency — enforceable stop thresholds beat LLM rationalizations to continue.
