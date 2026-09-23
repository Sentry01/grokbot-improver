#!/usr/bin/env python3
"""route-tool-subagent gate — thin wrapper around shared runner."""
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
    default = (config.get("thresholds") or {}).get("default_route", "answer_inline")
    route_ans = answers.get("route") or {}
    choice = route_ans.get("choice") or default
    conf = route_ans.get("confidence")
    probs = route_ans.get("probabilities") or {}
    return {
        "action": choice,
        "proceed": True,
        "reason": f"route choice={choice} confidence={conf}",
        "route": choice,
        "confidence": conf,
        "probabilities": probs,
        "default_route": default,
    }


def decide(state: dict) -> dict:
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
