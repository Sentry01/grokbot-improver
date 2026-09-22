# Grok×Jev Efficiency Gates

Agent-ops decision gates powered by Jev (`jev-latest` via TypeSafe System One).  
Agent still drafts; Jev gates, ranks, and routes.  
**Source of truth:** `../cool-use-cases.md` (question maps / state shapes).  
**Scope:** agent-ops & product intelligence only — not portfolio / macro.

## Layout

```
gates/
  common/
    jev_client.py   # POST https://api.typesafe.ai/v1/systemone ; Bearer $TYPESAFE_API_KEY; fail soft
    runner.py       # load config + state, call Jev, evaluate(), write dry/
  <slug>/
    SPEC.md
    config.json     # questions, thresholds, fail_mode, defaults
    gate.py         # cd gates/<slug> && python gate.py
    example_state.json
    dry/            # one live dry result per gate
  README.md
  INDEX.md          # all 15 gates + thresholds
```

## How an agent should wire these

Suggested harness (from cool-use-cases):

```
user goal
  → [3] route-tool-subagent
  → loop:
       → [1] tool-worth-it / [15] redundant-tool-call / [10] auto-review-prescreen
       → tool
       → [6] search-fetch-triage / [13] browser-page-relevance
       → [4] stop-vs-continue
  → draft
  → [14] draft-completeness / [2] send-to-user-quality
  → [5] ask-vs-act
  → SendToUser
```

Side paths:
- **Inbound:** [7] inbound-noise-triage on mail / Slack / files / mentions
- **Delegation:** [8] executor-spawn before Task; [9] parallel-fanout before multi-tool batches
- **Memory / routines:** [11] memory-save after learning; [12] routine-skill-schedule after repeatable workflows

### Before expensive tools
Call `tool-worth-it` and optionally `redundant-tool-call` + `auto-review-prescreen`. Skip or shrink when decide says so.

### Before SendToUser / external send
Call `draft-completeness` then `send-to-user-quality`. Hold on fail-closed / revise.

### Before Task / executor spawn
Call `executor-spawn`. Prefer inline when noul low or reason=`underspecified`.

### Before parallel multi-tool messages
Call `parallel-fanout` for independence + concurrency cap.

## Usage

```bash
export TYPESAFE_API_KEY=...   # never logged / never printed
cd gates/<slug> && python gate.py   # dry-run with example_state.json → dry/
```

Importable:

```python
import sys
sys.path.insert(0, "/workspace/grok-jev-efficiency-scout/gates/<slug>")
import gate
outcome = gate.decide({...})
# outcome["decision"]["action"], outcome["answers"], ...
```

## Constraints

- Question types: `noul` / `score` / `choice` only — no free-text
- Never print `TYPESAFE_API_KEY`
- Fail soft with clear logs; `gate.py` exits 0 even on API error
- Fail-open vs fail-closed documented per SPEC / INDEX

See `INDEX.md` for the full table of 15 gates.
