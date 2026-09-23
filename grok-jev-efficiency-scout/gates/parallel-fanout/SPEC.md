# Gate: parallel-fanout

**Name:** Parallel Fan-out Orchestrator  
**Slug:** `parallel-fanout`  
**Rank / source:** #9 in `cool-use-cases.md`  
**Primary lever:** latency

## Purpose

Decide whether proposed next actions are independent enough to run in parallel, and how wide the fan-out should be — without runaway floods.

## When to call

Planner step before a multi-tool message.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `proposed` | string[] | Proposed next actions |
| `dependencies` | string | Known deps summary |
| `rate_limit_pressure` | string | low / medium / high |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `fan_out_ok` | `noul` | Independent enough to parallelize |
| `max_parallel_bucket` | `score` | strictly serial → pair only → small batch → wide fan-out |

No free-text questions.

## Thresholds

- **Parallel** if `fan_out_ok.noul >= 0.6` and score implies cap > 1
- Cap hint from score: `<0.5→1`, `≥0.5→2`, `≥1.5→5`, `≥2.5→8`
- Else **sequential**

## Fail mode

**Fail-open** → `sequential` on API error (safest for rate limits / Auto-review).

## Expected efficiency win

Latency — structured parallelism that composes with harness limits.
