# Gate: executor-spawn

**Name:** Executor Spawn Gate  
**Slug:** `executor-spawn`  
**Rank / source:** #8 in `cool-use-cases.md`  
**Primary lever:** cost / latency

## Purpose

Decide whether to spawn a dedicated executor subagent vs doing the work inline. Avoids spawn overhead for tiny tasks and missed spawns for long autonomous work.

## When to call

Before Task / executor launch.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `task` | string | Delegated task summary |
| `est_steps` | number | Rough step count |
| `needs_own_browser` | bool | Needs isolated desktop |
| `parent_blocked_on_result` | bool | Parent waiting |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `spawn_executor` | `noul` | Worth spawning |
| `reason` | `choice` | `long_horizon`, `isolation`, `parallel`, `inline_enough`, `underspecified` |

No free-text questions.

## Thresholds

- **Spawn** if `spawn_executor.noul >= 0.65` **AND** `reason != underspecified`
- Else **inline**

## Fail mode

**Fail-open** → `inline` for small / uncertain tasks on API error (cheaper/safer default).

## Expected efficiency win

Cost + latency — calibrated spawn gate + reason for logging/policy.
