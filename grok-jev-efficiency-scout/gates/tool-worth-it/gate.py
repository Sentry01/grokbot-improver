#!/usr/bin/env python3
"""tool-worth-it gate — thin wrapper around shared runner."""
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
    thr = (config.get("thresholds") or {}).get("tool_worth_it_min", 0.65)
    tw = answers.get("tool_worth_it") or {}
    noul = tw.get("noul")
    blocker = (answers.get("primary_blocker") or {}).get("choice")
    if noul is None:
        return {
            "action": "run_tool",
            "proceed": True,
            "reason": "missing tool_worth_it noul; fail-open",
            "noul": None,
            "primary_blocker": blocker,
            "threshold": thr,
        }
    proceed = float(noul) >= float(thr)
    return {
        "action": "run_tool" if proceed else "skip_tool",
        "proceed": proceed,
        "reason": (
            f"tool_worth_it noul={noul} >= {thr}"
            if proceed
            else f"tool_worth_it noul={noul} < {thr}; blocker={blocker}"
        ),
        "noul": noul,
        "primary_blocker": blocker,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
