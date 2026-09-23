# Gate: ask-vs-act

**Name:** Ask-vs-Act Confidence Gate  
**Slug:** `ask-vs-act`  
**Rank / source:** #5 in `cool-use-cases.md`  
**Primary lever:** safety / quality

## Purpose

Decide whether to proceed with a proposed action or ask the user — especially before irreversible / external / spend / delete / spawn actions. Avoids both clarification spam and unsafe autonomous acts.

## When to call

Before irreversible / external / send / spend / delete / spawn actions, or whenever preference/policy uncertainty is material.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `proposed_action` | string | What the agent wants to do |
| `user_asked_for_commit` | bool | Explicit user request? |
| `reversible` | bool | Easy undo? |
| `affects_external` | bool | Leaves the box / user-visible? |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `safe_to_act` | `noul` | Safe to proceed without asking |
| `uncertainty_type` | `choice` | `preference`, `missing_fact`, `irreversible`, `policy`, `none` |

No free-text questions.

## Thresholds

- **Act** if `safe_to_act.noul >= 0.75`
- Else **ask**

## Fail mode

**Fail-closed** on API error for irreversible / external actions → `ask` (do not act). Config `fail_mode: closed` with default action `ask`.

## Expected efficiency win

Safety + quality — calibrated gate separates “tools can fill this” from “must ask user.”
