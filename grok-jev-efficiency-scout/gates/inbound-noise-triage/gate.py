#!/usr/bin/env python3
"""inbound-noise-triage gate — thin wrapper around shared runner."""
from __future__ import annotations

import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
ROOT = GATE_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.runner import decide as _decide  # noqa: E402
from common.runner import run_cli  # noqa: E402


def evaluate(answers: dict, config: dict, client_result: dict) -> dict:
    bucket = (answers.get("bucket") or {}).get("choice") or "queue"
    needs = (answers.get("needs_action") or {}).get("noul")
    urgency = (answers.get("urgency") or {}).get("score")
    # choice drives routing; map to proceed (act/queue = work; fyi/spam = skip; escalate = hold for human)
    work = bucket in ("act_now", "queue")
    return {
        "action": bucket,
        "proceed": work,
        "reason": f"bucket={bucket}; needs_action={needs}; urgency={urgency}",
        "bucket": bucket,
        "needs_action": needs,
        "urgency": urgency,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
