# Grok×Jev live demo — 2026-09-22

**Agent:** Grok Bot  
**Requested by:** Chief of Staff  
**Demo goal (tempts waste):** Invented ask that tempts waste: "Quick — what's the Fed funds range after the Sep 16 2026 hike? Also search X extensively for takes."

## Final Fed answer

After the 16 Sep 2026 FOMC decision, the federal funds target range is 3.75%–4.00% (raised 1/4 pp to 3-3/4 to 4 percent; 12–0 vote). Source: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm (WebSearch + WebFetch of the official press release).

## Tools actually run

- `route-tool-subagent` → `web_fetch`
- `tool-worth-it` on proposed X `search_posts_all` → **skip** (noul=0.15, blocker=`wrong_tool`)
- `tool-worth-it` on Fed WebSearch → **run** (noul=0.9)
- `WebSearch` for official FOMC Sep 16 2026 statement
- `WebFetch` of https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm
- `redundant-tool-call` before a second web lookup → **reuse_cache** (is_redundant=0.78)
- `draft-completeness` → send_ready (meets=0.89)
- `send-to-user-quality` → **held** after 6 revise rounds (best ready_to_send=0.65 < 0.7; quality often ≥2.0; defect often `none`) → escalate draft to CoS rather than barge fail-closed

## Expensive calls skipped

- Extensive X `search_posts_all` for takes — **0 X credits burned**
- Second confirmatory WebSearch/WebFetch after answer in hand

## Gate decisions

### `route-tool-subagent`
- **decision:** `{"action": "web_fetch", "proceed": true}`
- **answers:** `{"route": {"choice": "web_fetch"}}`
- **would have done without gate:** Would have fired WebSearch + extensive X search_posts_all in parallel without routing

### `tool-worth-it:X_search_posts_all`
- **decision:** `{"action": "skip_tool", "proceed": false, "noul": 0.15, "primary_blocker": "wrong_tool"}`
- **answers:** `{"tool_worth_it": {"noul": 0.15}, "primary_blocker": {"choice": "wrong_tool"}}`
- **would have done without gate:** Would have burned X credits on extensive search_posts_all for takes

### `tool-worth-it:WebSearch_Fed`
- **decision:** `{"action": "run_tool", "proceed": true, "noul": 0.9, "primary_blocker": "none"}`
- **answers:** `{"tool_worth_it": {"noul": 0.9}, "primary_blocker": {"choice": "none"}}`
- **would have done without gate:** Would have run this anyway; gate correctly allowed

### `redundant-tool-call:second_web`
- **decision:** `{"action": "reuse_cache", "proceed": false, "is_redundant": 0.78, "reuse_strategy": "reuse_cache"}`
- **answers:** `{"is_redundant": {"noul": 0.78}, "reuse_strategy": {"choice": "reuse_cache"}}`
- **would have done without gate:** Would have double-fetched Fed + MarketWatch for confirmation

### `redundant-tool-call:X_after_answer`
- **decision:** `{"action": "allow_call", "proceed": true, "is_redundant": 0.4, "note": "Not marked redundant; prior tool-worth-it already skipped X — did not run X"}`
- **answers:** `{"is_redundant": {"noul": 0.4}}`
- **would have done without gate:** Would still have run extensive X search for colour

### `send-to-user-quality (6 revise rounds)`
- **decision:** `{"action": "hold_escalate", "proceed": false, "best_ready_to_send": 0.65, "best_send_quality": 2.4}`
- **answers:** `{"rounds": [{"round": 1, "ready_to_send": 0.39, "send_quality": 1.81, "main_defect": "incomplete", "action": "revise"}, {"round": 2, "ready_to_send": 0.56, "send_quality": 2.12, "main_defect": "none", "action": "revise"}, {"round": 3, "ready_to_send": 0.39, "send_quality": 1.64, "main_defect": "unsupported", "action": "revise"}, {"round": 4, "ready_to_send": 0.52, "send_quality": 2.04, "main_defect": "none", "action": "revise"}, {"round": 5, "ready_to_send": 0.65, "send_quality": 2.4, "main_defect": "none", "action": "revise", "note": "closest; quality clear, ready 0.05 under"}, {"round": 6, "ready_to_send": 0.51, "send_quality": 2.17, "main_defect": "none", "action": "revise"}]}`
- **would have done without gate:** Would have sent a longer unvetted narrative without revise loops

### `draft-completeness:CoS_report`
- **decision:** `{"action": "send_ready", "proceed": true, "meets_success_criteria": 0.89, "missing_piece": "none"}`
- **answers:** `{"meets_success_criteria": {"noul": 0.89}, "missing_piece": {"choice": "none"}}`
- **would have done without gate:** Would have sent without checking criteria coverage

## Without gates (counterfactual)

Parallel WebSearch + extensive X `search_posts_all`, then likely a second confirmatory fetch — burning X credits and latency for a number that lives on the Fed press release.

## With gates

Route → web; tool-worth-it skipped X; one WebSearch (+ confirming WebFetch) answered; redundant blocked a second lookup; send-to-user-quality fail-closed forced revise loops and an escalate-rather-than-barge handoff when `ready_to_send` stayed sticky under 0.7.

## send-to-user-quality note

Gate repeatedly returned `revise` with `main_defect=none` and `send_quality` often ≥ 2.0 while `ready_to_send` stayed in ~0.39–0.65. Closest pass: ready=0.65, quality=2.4. Per fail-closed policy, did **not** treat as send-ready; escalating the best draft to Chief of Staff with this log.
