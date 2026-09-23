#!/usr/bin/env python3
"""ask-vs-act gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("safe_to_act_min", 0.75))
    safe = (answers.get("safe_to_act") or {}).get("noul")
    unc = (answers.get("uncertainty_type") or {}).get("choice")

    if safe is None:
        return {
            "action": "ask",
            "proceed": False,
            "reason": "missing safe_to_act; fail-closed ask",
            "safe_to_act": None,
            "uncertainty_type": unc,
            "threshold": thr,
        }

    act = float(safe) >= thr
    return {
        "action": "act" if act else "ask",
        "proceed": act,
        "reason": (
            f"safe_to_act={safe} >= {thr}; uncertainty={unc}"
            if act
            else f"safe_to_act={safe} < {thr}; ask user (uncertainty={unc})"
        ),
        "safe_to_act": safe,
        "uncertainty_type": unc,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
