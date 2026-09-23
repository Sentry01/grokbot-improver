# Gate: tool-worth-it

**Name:** Tool Worth-It Gate  
**Slug:** `tool-worth-it`  
**Rank / source:** #1 in `cool-use-cases.md`  
**Primary lever:** cost / latency

## Purpose

Before firing an expensive tool (X search, WebFetch, browser, Shell, executor spawn), ask Jev whether the call is likely to *materially* improve the answer beyond what state already holds. Skip wasteful “just in case” calls.

## When to call

Immediately before a tool / MCP / browser / Shell call in exploratory loops, especially after a first answer already covers the ask.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `user_goal` | string | What the user wants |
| `already_have` | string | Evidence / context already in turn |
| `proposed_tool` | string | Intent of the next tool call |
| `est_cost_tier` | string | e.g. `low` / `medium` / `high` |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `tool_worth_it` | `noul` | Belief that the tool will materially help |
| `primary_blocker` | `choice` | Why not (telemetry); criteria: `already_answered`, `wrong_tool`, `low_signal`, `user_not_needed`, `none` |

No free-text questions.

## Thresholds

- **Proceed** (run the tool) if `tool_worth_it.noul >= 0.65`
- Else **skip** (use `primary_blocker.choice` for logs)

## Fail mode

**Fail-open** on API error → `proceed=true` / action `run_tool` so we do not block work when Jev is down.

## Expected efficiency win

Largest $ / latency lever on X / web / browser paths — calibrated skip without another full reasoning pass.
