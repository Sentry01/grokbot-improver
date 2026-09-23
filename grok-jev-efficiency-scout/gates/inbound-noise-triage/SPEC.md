# Gate: inbound-noise-triage

**Name:** Inbound Noise Triage (email / Slack / files)  
**Slug:** `inbound-noise-triage`  
**Rank / source:** #7 in `cool-use-cases.md`  
**Primary lever:** latency / quality

## Purpose

Triage inbound mentions, mail, Slack, and file drops into stable buckets so agents do not context-switch into FYI noise.

## When to call

Inbox polling / mention handlers / file-drop watchers at the start of a turn.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `channel` | string | slack / email / file / mention |
| `from` | string | Sender |
| `text` | string | Body / title |
| `thread_context` | string | Short context |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `needs_action` | `noul` | Requires action this turn |
| `bucket` | `choice` | `act_now`, `queue`, `fyi`, `spam_noise`, `escalate_human` |
| `urgency` | `score` | ignore → low → normal → high → critical |

No free-text questions.

## Thresholds

- **Route by `bucket.choice`** (primary)
- `proceed=true` for `act_now` / `queue`; false for `fyi` / `spam_noise` / `escalate_human`
- `needs_action` / `urgency` are telemetry for harness priority

## Fail mode

**Fail-open** → `queue` on API error (do not drop real work; do not auto-act).

## Expected efficiency win

Latency + quality — stable buckets for routing rules; batch-score an inbox.
