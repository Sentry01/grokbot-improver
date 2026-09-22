# Gate: routine-skill-schedule

**Name:** Routine / Skill Schedule Decision  
**Slug:** `routine-skill-schedule`  
**Rank / source:** #12 in `cool-use-cases.md`  
**Primary lever:** quality (ops hygiene)

## Purpose

Decide whether a workflow should become a scheduled routine/skill and at what cadence — avoid calendar spam and missed recurring work.

## When to call

After defining a repeatable workflow.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `task` | string | Candidate routine |
| `repeat_value` | string | low / medium / high |
| `cost_per_run` | string | low / medium / high |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `worth_scheduling` | `noul` | Should schedule |
| `cadence` | `choice` | `hourly`, `daily`, `weekly`, `on_event`, `do_not_schedule` |

No free-text questions.

## Thresholds

- **Schedule** if `worth_scheduling.noul >= 0.7` AND `cadence != do_not_schedule`
- Action becomes the cadence label; else `do_not_schedule`

## Fail mode

**Fail-closed** → `do_not_schedule` on API error (do not create routines when unsure).

## Expected efficiency win

Quality / ops hygiene — cadence as constrained choice + noul gate.
