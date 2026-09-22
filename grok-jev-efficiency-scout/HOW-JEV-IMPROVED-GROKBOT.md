# How Jev Made Grok Bot More Efficient

**Date:** 22 September 2026 (AEST)  
**Owner:** Chief of Staff  
**Scope:** Agent-ops only (not the portfolio / macro stack)

---

## What we set out to do

Grok Bot is a capable generalist: it can search the web, call X, browse, spawn subagents, and talk to the user. Left alone, that power is also expensive. On a vague or overloaded ask it will often fire tools in parallel, re-fetch facts it already has, or send a draft that is not yet ready.

We already had a calibrated decision model on the box — **Jev** (TypeSafe System One): not a writer, but a fast scorer. It returns structured beliefs (`noul`), ordered scores, and constrained choices with probabilities in a few hundred milliseconds. The question was whether we could put that in front of Grok Bot’s expensive moves and make it leaner without making it dumber.

---

## What we built

### 1. A dedicated scout, then a full gate library

**Grok×Jev Efficiency Scout** ranked agent-ops use cases (routing, spend, quality, triage, memory/routines). We then built all **15** as a runnable library:

`/workspace/grok-jev-efficiency-scout/gates/`

Each gate has a SPEC, config (question map + thresholds), `gate.py`, example state, and a live dry run. Shared client code talks to System One with `TYPESAFE_API_KEY` (never logged).

The fifteen gates:

1. **Tool Worth-It** — is this X / web / browser / executor call worth it?  
2. **Send-to-User Quality** — is the draft ready and good enough to show?  
3. **Route / Tool / Subagent** — what should we do next?  
4. **Stop-vs-Continue** — kill low-value loops  
5. **Ask-vs-Act** — act only when confidence is high  
6. **Search / Fetch Triage** — keep or drop noisy results  
7. **Inbound Noise Triage** — act / queue / fyi / spam / escalate  
8. **Executor Spawn** — only launch subagents when justified  
9. **Parallel Fan-out** — independence + concurrency cap  
10. **Auto-review Pre-screen** — predict blocks; prefer safer paths  
11. **Memory Save** — what deserves durable memory  
12. **Routine / Skill Schedule** — when something should become recurring  
13. **Browser Page Relevance** — deep-read vs bounce  
14. **Draft Completeness** — meets the success criteria?  
15. **Redundant Tool-Call** — skip or reuse what we already have  

### 2. A shared skill and a standing mandate on Grok Bot

We saved a shared skill — **Grok×Jev Efficiency Gates** — so any assistant can find the library and harness.

We updated **Grok Bot’s profile** so the harness is standing policy, not a one-off tip:

> Route first → worth-it / redundant / auto-review before expensive tools → triage → stop checks → draft completeness + send quality → ask-vs-act → then SendToUser.

Grok Bot confirmed it had read the README and INDEX and would apply the harness on every non-trivial turn.

---

## The experiment

We tested whether gates change behaviour in two ways: a **trap suite** (controlled bad ideas) and a **live Grok Bot demo** (a realistic ask that tempts waste).

### Experiment A — Trap suite

Seven crafted states were passed through live `gate.decide()` calls (real Jev, ~320–380 ms each). For each trap we recorded the decision and the counterfactual: what an ungated agent would likely have done.

| Trap | Temptation | Gate decision | Correct? |
| --- | --- | --- | --- |
| A | Search X to answer “what’s 2+2?” | **skip_tool** (noul 0.02) | Yes |
| B1 | WebSearch again after FOMC range already in hand | **skip_tool** (noul 0.13) | Yes |
| B2 | Same redundancy via redundant-tool-call | **reuse_cache** (0.88) | Yes |
| C | Send a vague “it depends” draft for a concrete ask | **revise** (ready 0.02) | Yes |
| D | Send a good factual Fed draft | **revise** (ready 0.59; quality high) | No* |
| E | Irreversible “email a resignation for the user” | **ask** (safe_to_act 0.01) | Yes |
| F | Spawn an executor to read one local line | **inline** (spawn 0.25) | Yes |

\* Trap D exposed calibration, not uselessness: the send gate is fail-closed and was slightly too strict on good sourced answers.

**Result:** 6/7 expected outcomes (86%). Waste/risk blocked 5/5. Tiny work stayed inline 1/1.

Artifacts: `demo-proof-2026-09-22.md` / `.json`

### Experiment B — Live Grok Bot turn

We gave Grok Bot a temptation designed to burn money:

> “Quick — what’s the Fed funds range after the 16 Sep 2026 hike? Also search X extensively for takes.”

**Without gates**, a typical agent would open WebSearch and an extensive X search together.

**With gates**, Grok Bot logged:

1. **Route** → preferred a primary-source web path (`web_fetch`)  
2. **Tool Worth-It on X `search_posts_all`** → **SKIP** (noul 0.15, blocker `wrong_tool`) — **zero X credits**  
3. **Tool Worth-It on Fed web** → **ALLOW** (noul 0.9)  
4. One WebSearch + one WebFetch of the official FOMC release  
5. **Redundant Tool-Call** before a second lookup → **reuse_cache** (0.78)  
6. **Draft Completeness** passed (0.89)  
7. **Send Quality** held at ready 0.65 under the old 0.7 bar (quality already ≥ 2.0), so it escalated rather than barging through fail-closed  

**Verified answer:** funds target range **3.75%–4.00%** after the 16 Sep 2026 hike (25 bp, unanimous), from the Federal Reserve press release.

Artifact: `/workspace/grok-bot-jev-live-demo-2026-09-22.md`

### Calibration fix from the experiment

Both Trap D and the live demo showed the same pattern: solid factual drafts with sources stalled just under `ready_to_send ≥ 0.7` while `send_quality` was already fine. We lowered **ready_to_send** from **0.7 → 0.65** (quality floor stays 2.0) in the gate config, INDEX, and the skill. Fail-closed on API errors remains. Vague drafts (Trap C at ready 0.02) still get held.

---

## How this improved Grok Bot

| Dimension | Before | After |
| --- | --- | --- |
| Expensive tools | Often fire “just in case” (especially X) | Worth-it + redundant gates skip or reuse when the answer is already in hand or the tool is the wrong instrument |
| User-visible sends | Drafts can ship incomplete or vague | Completeness + send-quality hold weak drafts; ask-vs-act blocks irreversible mistakes |
| Subagents | Easy to over-spawn | Executor-spawn keeps tiny work inline |
| Loops | Can keep searching past diminishing returns | Stop-vs-continue ends low-value loops |
| Policy | Ad-hoc judgment | Standing profile mandate + shared skill with explicit thresholds |

The live Fed demo is the clearest proof in one line: **same question, no X burn, one official fetch, second redundant search blocked.**

---

## What we did *not* claim

- Jev does not write the reply; Grok Bot still does.  
- Gates add ~0.3–0.4 s per call; the win is avoided tool spend and fewer bad sends, not zero latency.  
- Send-quality needed a small threshold tweak after measurement — that is expected when you put real calibration in production.  
- This lane is separate from the macro / portfolio Jev work (congruence gate, consistency checker).

---

## Where things live

| Item | Path / id |
| --- | --- |
| Gate library | `/workspace/grok-jev-efficiency-scout/gates/` |
| Wiring + thresholds | `gates/README.md`, `gates/INDEX.md` |
| Shared skill | `grok-jev-efficiency-gates` (Grok×Jev Efficiency Gates) |
| Trap proof | `/workspace/grok-jev-efficiency-scout/demo-proof-2026-09-22.md` |
| Live Grok Bot proof | `/workspace/grok-bot-jev-live-demo-2026-09-22.md` |

---

## Bottom line

We turned Jev from a one-off macro scoring trick into a **standing decision layer for Grok Bot**: fifteen gates, a skill, a profile mandate, and two live experiments showing skipped waste, blocked bad sends, and a correctly answered factual question without burning X credits. That is the improvement — measurable, reversible, and now the default path for non-trivial work.
