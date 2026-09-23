#!/usr/bin/env python3
"""executor-spawn gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("spawn_noul_min", 0.65))
    noul = (answers.get("spawn_executor") or {}).get("noul")
    reason = (answers.get("reason") or {}).get("choice")
    if noul is None:
        return {
            "action": "inline",
            "proceed": False,
            "reason": "missing spawn_executor; fail-open inline",
            "spawn_noul": None,
            "spawn_reason": reason,
            "threshold": thr,
        }
    # Policy: spawn only if noul>=thr AND reason != underspecified
    spawn = float(noul) >= thr and reason != "underspecified"
    return {
        "action": "spawn" if spawn else "inline",
        "proceed": spawn,
        "reason": (
            f"spawn: spawn_executor={noul} >= {thr}; reason={reason}"
            if spawn
            else f"inline: spawn_executor={noul} (min {thr}) reason={reason}"
        ),
        "spawn_noul": noul,
        "spawn_reason": reason,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
