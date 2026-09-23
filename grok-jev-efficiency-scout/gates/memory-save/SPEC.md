# Gate: memory-save

**Name:** Memory Save Decision  
**Slug:** `memory-save`  
**Rank / source:** #11 in `cool-use-cases.md`  
**Primary lever:** quality / cost

## Purpose

Decide whether a learned fact is worth durable agent memory — prevent bloat and refuse credential storage.

## When to call

After learning moments / end of successful workflows.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `candidate` | string | Fact candidate |
| `already_in_memory` | bool | |
| `session_only` | bool | |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `should_save` | `noul` | Worth durable memory |
| `memory_kind` | `choice` | `user_preference`, `api_quirk`, `procedure`, `ephemeral`, `secret` |

No free-text questions.

## Thresholds

- **Refuse** if `memory_kind=secret`
- **Skip** if `memory_kind=ephemeral`
- Else **save** if `should_save.noul >= 0.7`
- Else **skip_save**

## Fail mode

**Fail-open** → `skip_save` on API error (do not bloat memory when unsure).

## Expected efficiency win

Quality + cost — fewer re-discovers without memory spam.
