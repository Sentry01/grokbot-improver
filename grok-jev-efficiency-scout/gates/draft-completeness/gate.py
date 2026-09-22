#!/usr/bin/env python3
"""draft-completeness gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("meets_criteria_min", 0.7))
    noul = (answers.get("meets_success_criteria") or {}).get("noul")
    missing = (answers.get("missing_piece") or {}).get("choice")
    if noul is None:
        return {
            "action": "polish",
            "proceed": False,
            "reason": "missing meets_success_criteria; fail-open polish",
            "meets_success_criteria": None,
            "missing_piece": missing,
            "threshold": thr,
        }
    complete = float(noul) >= thr and missing in (None, "none")
    if complete:
        action = "send_ready"
        proceed = True
        reason = f"complete: meets_success_criteria={noul} >= {thr}; missing={missing}"
    elif float(noul) >= thr * 0.85 and missing not in (None, "none"):
        action = "polish"
        proceed = False
        reason = f"near-complete polish: noul={noul}; missing={missing}"
    else:
        action = "revise"
        proceed = False
        reason = f"incomplete: meets_success_criteria={noul} (min {thr}); missing={missing}"
    return {
        "action": action,
        "proceed": proceed,
        "reason": reason,
        "meets_success_criteria": noul,
        "missing_piece": missing,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
