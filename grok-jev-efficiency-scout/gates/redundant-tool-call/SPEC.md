# Gate: redundant-tool-call

**Name:** Redundant Tool-Call Detector  
**Slug:** `redundant-tool-call`  
**Rank / source:** #15 in `cool-use-cases.md`  
**Primary lever:** cost

## Purpose

Detect re-fetching the same URL, re-listing the same dir, or near-identical searches when state already holds the answer.

## When to call

Before a tool call, with a rolling tool-result digest in state. Pairs with `tool-worth-it`.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `proposed` | string | Proposed tool call |
| `recent` | string[] | Recent tool results digest |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `is_redundant` | `noul` | Redundant with recent results |
| `reuse_strategy` | `choice` | `reuse_cache`, `narrow_delta`, `different_source`, `not_redundant` |

No free-text questions.

## Thresholds

- **Skip / reuse** if `is_redundant.noul >= 0.65` AND strategy ≠ `not_redundant`
- Action follows `reuse_strategy` (`reuse_cache` proceed=false; `narrow_delta`/`different_source` may proceed)
- Else **allow_call**

## Fail mode

**Fail-open** → `allow_call` on API error (do not block needed work).

## Expected efficiency win

Cost — explicit redundancy noul is easy to log and threshold.
