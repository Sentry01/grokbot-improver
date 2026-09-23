# Gate: route-tool-subagent

**Name:** Route / Tool / Subagent Choice  
**Slug:** `route-tool-subagent`  
**Rank / source:** #3 in `cool-use-cases.md`  
**Primary lever:** latency / cost

## Purpose

Pick the cheapest safe next action (inline answer vs fetch vs search vs browser vs shell vs executor vs ask user) without inventing free-text tool names.

## When to call

Planner step / before tool selection when multiple routes are plausible.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `goal` | string | Current micro-goal |
| `known_urls` | string[] | URLs already known |
| `have_api_key_env` | bool | Whether needed secrets are present |
| `prior_failures` | string[] | Recent failed routes |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `route` | `choice` | Winner among constrained routes |

Criteria labels: `answer_inline`, `web_fetch`, `web_search`, `x_search`, `browser`, `shell_local`, `spawn_executor`, `ask_user`.

No free-text questions.

## Thresholds

- Use **choice winner** (`route.choice`) as the action.
- Soft routing: if `route.confidence` is low, harness may try top-2 from `probabilities` (documented; not enforced in evaluate).

## Fail mode

**Fail-open** → default `answer_inline` (cheapest safe) on API error.

## Expected efficiency win

Latency + cost — constrained choice prevents wrong-tool cascades.
