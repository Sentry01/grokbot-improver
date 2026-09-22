# Efficiency Gates Index (all 15)

As-of: 2026-09-22 AEST · Source: `cool-use-cases.md`

| # | Slug | Name | Key threshold(s) / decision | Fail mode | Default on error | Decision fields |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `tool-worth-it` | Tool Worth-It Gate | `tool_worth_it` noul ≥ **0.65** → run tool | **open** | `run_tool` | `action`, `proceed`, `noul`, `primary_blocker` |
| 2 | `send-to-user-quality` | Send-to-User Quality Gate | `ready_to_send` ≥ **0.65** AND `send_quality` ≥ **2.0** → send | **closed** (external); open for optional chat polish | `hold_send` | `action`, `proceed`, `ready_to_send`, `send_quality`, `main_defect` |
| 3 | `route-tool-subagent` | Route / Tool / Subagent Choice | use `route` choice winner | **open** | `answer_inline` | `action`, `route`, `confidence`, `probabilities` |
| 4 | `stop-vs-continue` | Stop-vs-Continue Loop Gate | stop if `should_stop` ≥ **0.6** OR `marginal_value` < **1.5** | **open** | `continue` once | `action`, `proceed`, `should_stop`, `marginal_value` |
| 5 | `ask-vs-act` | Ask-vs-Act Confidence Gate | act if `safe_to_act` ≥ **0.75**; else ask | **closed** | `ask` | `action`, `proceed`, `safe_to_act`, `uncertainty_type` |
| 6 | `search-fetch-triage` | Search / Fetch Result Triage | keep if `keep` ≥ **0.55** OR `utility` ≥ **1.5** | **open** | `keep` (top-N) | `action`, `proceed`, `keep_noul`, `utility` |
| 7 | `inbound-noise-triage` | Inbound Noise Triage | `bucket` choice drives route | **open** | `queue` | `action`(=bucket), `proceed`, `needs_action`, `urgency` |
| 8 | `executor-spawn` | Executor Spawn Gate | spawn if `spawn_executor` ≥ **0.65** AND reason≠underspecified | **open** | `inline` | `action`, `proceed`, `spawn_noul`, `spawn_reason` |
| 9 | `parallel-fanout` | Parallel Fan-out Orchestrator | parallel if `fan_out_ok` ≥ **0.6**; cap via `max_parallel_bucket` | **open** | `sequential` | `action`, `proceed`, `fan_out_noul`, `max_parallel` |
| 10 | `auto-review-prescreen` | Auto-review Risk Pre-screen | if `likely_blocked` ≥ **0.55** prefer `safer_path` | **open** | `proceed_with_caution` | `action`, `proceed`, `likely_blocked`, `safer_path` |
| 11 | `memory-save` | Memory Save Decision | save if `should_save` ≥ **0.7** (refuse `secret`) | **open** | `skip_save` | `action`, `proceed`, `should_save`, `memory_kind` |
| 12 | `routine-skill-schedule` | Routine / Skill Schedule Decision | schedule if `worth_scheduling` ≥ **0.7** + cadence | **closed** | `do_not_schedule` | `action`(=cadence), `proceed`, `worth_scheduling`, `cadence` |
| 13 | `browser-page-relevance` | Browser Page Relevance Gate | continue if `page_worth_deep_read` ≥ **0.6**; follow choice | **open** | `extract_now` once | `action`, `proceed`, `page_worth`, `next_browse_action` |
| 14 | `draft-completeness` | Draft Completeness Gate | send_ready if `meets_success_criteria` ≥ **0.7** AND missing=`none` | **open** | `polish` | `action`, `proceed`, `meets_success_criteria`, `missing_piece` |
| 15 | `redundant-tool-call` | Redundant Tool-Call Detector | skip/reuse if `is_redundant` ≥ **0.65** | **open** | `allow_call` | `action`, `proceed`, `is_redundant`, `reuse_strategy` |

## Paths

Shared: `gates/common/jev_client.py`, `gates/common/runner.py`

```
gates/tool-worth-it/
gates/send-to-user-quality/
gates/route-tool-subagent/
gates/stop-vs-continue/
gates/ask-vs-act/
gates/search-fetch-triage/
gates/inbound-noise-triage/
gates/executor-spawn/
gates/parallel-fanout/
gates/auto-review-prescreen/
gates/memory-save/
gates/routine-skill-schedule/
gates/browser-page-relevance/
gates/draft-completeness/
gates/redundant-tool-call/
```

## Dry runs

Each slug has exactly one live dry under `gates/<slug>/dry/` written by `python gate.py`.
