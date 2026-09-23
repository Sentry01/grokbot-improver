# Gate: send-to-user-quality

**Name:** Send-to-User Quality Gate  
**Slug:** `send-to-user-quality`  
**Rank / source:** #2 in `cool-use-cases.md`  
**Primary lever:** quality / safety

## Purpose

Block incomplete, unsupported, or wrong-tone drafts from landing on user-visible channels (SendToUser, email, Slack) before evidence is in.

## When to call

Immediately before SendToUser / outbound email / Slack post / any external send.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `channel` | string | e.g. `SendToUser`, `email`, `slack`, `chat_polish` |
| `goal` | string | Stated deliverable |
| `draft_excerpt` | string | Short excerpt of the draft |
| `open_todos` | string[] | Remaining work |
| `evidence_sources` | array of `{tool, claim, excerpt}` | **Optional.** Tool/state provenance for material claims in the draft. Empty or omitted → treat factual claims carefully (may score as `unsupported`). When populated entries cover the draft’s material claims, `main_defect` should prefer `none` and `ready_to_send` should reflect that evidence is already in-state (no further tool use required for those claims). |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `ready_to_send` | `noul` | Ready without further tool use / rewrite |
| `send_quality` | `score` | Ordered: do-not-send → major rewrite → minor polish → send as-is |
| `main_defect` | `choice` | `incomplete`, `unsupported`, `wrong_scope`, `tone`, `none` |

No free-text questions.

## Thresholds

- **Send** if `ready_to_send.noul >= 0.65` **AND** `send_quality.score >= 2.0`
- Else **revise** (hold send; use `main_defect` for rewrite focus)

## Fail mode

- **Fail-closed** for external / irreversible sends (`channel` in `SendToUser`, `email`, `slack`, or when `external_send=true`) → block on API error.
- **Fail-open** for optional chat polish (`channel=chat_polish` or `external_send=false`) → allow draft through on API error.

Config default is fail-closed (`fail_mode: closed`) because the example channel is SendToUser. Gate `evaluate` / `decide` also inspects `state.channel` when provided via the client result request state; dry runs use config `fail_mode`.

For importable `decide(state)`, callers should set `channel` appropriately; on API error the runner uses config `fail_mode` (closed). Optional polish callers can override by using a fork or setting config — documented here so harnesses know: **external = closed, chat polish optional = open**.

## Expected efficiency win

Quality + safety — separate calibrated critique beats same-model self-review bias.
