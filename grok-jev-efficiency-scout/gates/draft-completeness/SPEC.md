# Gate: draft-completeness

**Name:** Draft Completeness Gate  
**Slug:** `draft-completeness`  
**Rank / source:** #14 in `cool-use-cases.md`  
**Primary lever:** quality

## Purpose

Catch partial deliverables presented as done (missing files, sections, dry-call evidence, ranking).

## When to call

Before final user report / handoff; often paired with `send-to-user-quality`.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `success_criteria` | string[] | Checklist |
| `present_files` | string[] | What’s on disk |
| `dry_calls_done` | bool | |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `meets_success_criteria` | `noul` | Checklist met |
| `missing_piece` | `choice` | `files`, `content_section`, `verification`, `ranking`, `none` |

No free-text questions. (cool-use-cases uses noul+choice; completeness scored via noul.)

## Thresholds

- **send_ready** if `meets_success_criteria.noul >= 0.7` AND `missing_piece` in `{none, null}`
- Else **polish** / **revise** based on gap severity

## Fail mode

**Fail-open** → `polish` on API error (do not claim done).

## Expected efficiency win

Quality — typed checklist beats self-congratulatory “done” prose.
