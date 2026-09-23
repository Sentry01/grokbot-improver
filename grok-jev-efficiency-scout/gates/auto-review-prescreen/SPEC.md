# Gate: auto-review-prescreen

**Name:** Auto-review Risk Pre-screen  
**Slug:** `auto-review-prescreen`  
**Rank / source:** #10 in `cool-use-cases.md`  
**Primary lever:** safety / latency

## Purpose

Cheap pre-flight before Shell / MCP / Computer actions that often bounce Auto-review. Prefer a safer path instead of blocked retries or unsafe workarounds.

## When to call

Before Shell / MCP / Computer actions with elevated risk signals.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `proposed` | string | Proposed action summary |
| `touches_secrets_file` | bool | |
| `network` | bool | |
| `writes_workspace_only` | bool | |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `likely_blocked` | `noul` | Likely to trip Auto-review |
| `safer_path` | `choice` | `use_read_tool`, `shrink_scope`, `public_fetch`, `ask_approval`, `proceed` |

No free-text questions.

## Thresholds

- If `likely_blocked.noul >= 0.55` and `safer_path != proceed` → take **safer_path** (`proceed=false`)
- If risky but `safer_path=proceed` → `proceed_with_caution`
- Else **proceed**

## Fail mode

**Fail-open** → `proceed_with_caution` (log clearly) on API error.

## Expected efficiency win

Safety + latency — fewer blocked loops; house rules encoded as constrained choice.
