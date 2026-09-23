# Gate: browser-page-relevance

**Name:** Browser Page Relevance Gate  
**Slug:** `browser-page-relevance`  
**Rank / source:** #13 in `cool-use-cases.md`  
**Primary lever:** cost / latency

## Purpose

Stop browse thrash — decide whether the current page is worth a deep read and what the next browse action should be.

## When to call

After navigation / before heavy extract. Pairs with `tool-worth-it` for non-browser paths.

## State schema (agent-ops only)

| Field | Type | Notes |
| --- | --- | --- |
| `goal` | string | |
| `url` | string | |
| `title` | string | |
| `snippet` | string | |

## Jev question map

| Key | Type | Role |
| --- | --- | --- |
| `page_worth_deep_read` | `noul` | Worth deep read |
| `next_browse_action` | `choice` | `extract_now`, `follow_one_link`, `back_to_search`, `stop_browse` |

No free-text questions.

## Thresholds

- If `page_worth_deep_read.noul >= 0.6` → follow `next_browse_action` (continue when extract/follow)
- Else prefer `back_to_search` / `stop_browse` from choice

## Fail mode

**Fail-open** → `extract_now` (continue once) on API error.

## Expected efficiency win

Cost + latency — stops wander after search clicks.
