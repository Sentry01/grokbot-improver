# Grok×Jev Efficiency Gates (contribution)

This tree adds the **Grok×Jev** efficiency gate library, continuous-improvement loop, demos, and write-ups developed for Grok Bot.

## Contents

- `grok-jev-efficiency-scout/` — full package
  - `gates/` — 15 runnable Jev gates + `INDEX.md` / `README.md`
  - `ci-loop/` — decision log schema, logger, baselines, CI loop docs
  - `cool-use-cases.md`, `top-10-brief.md` — use-case research
  - `demo-proof-*.md/.json`, `HOW-JEV-IMPROVED-GROKBOT.md` — experiment write-ups
  - `grok-bot-jev-live-demo-2026-09-22.md` — live Grok Bot gated turn log

## Secrets

**Do not commit API keys.** The client reads `TYPESAFE_API_KEY` from the environment only:

```bash
export TYPESAFE_API_KEY=...   # never commit
cd grok-jev-efficiency-scout/gates/<slug> && python gate.py
```

See `.gitignore` for excluded patterns (`.env`, key files, etc.).

## Trap D (2026-09-23)

`send-to-user-quality` takes optional `evidence_sources` (`[{tool, claim, excerpt}]`) so sourced drafts are not false-held as `unsupported`. `ready_to_send_min` stays **0.65**. See `grok-jev-efficiency-scout/ci-loop/proposals/proposal-2026-09-23.md` and `grok-jev-efficiency-scout/ci-loop/reports/2026-09-23-trap-d-evidence.md`.

## License / provenance

Internal agent-ops artifact for improving Grok Bot with TypeSafe System One (Jev). Not financial advice.
