#!/usr/bin/env python3
"""auto-review-prescreen gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("likely_blocked_min", 0.55))
    noul = (answers.get("likely_blocked") or {}).get("noul")
    safer = (answers.get("safer_path") or {}).get("choice") or "proceed"
    if noul is None:
        return {
            "action": "proceed_with_caution",
            "proceed": True,
            "reason": "missing likely_blocked; fail-open proceed_with_caution",
            "likely_blocked": None,
            "safer_path": safer,
            "threshold": thr,
        }
    risky = float(noul) >= thr
    if risky and safer != "proceed":
        action = safer
        proceed = False
        reason = f"likely_blocked={noul} >= {thr}; prefer safer_path={safer}"
    elif risky and safer == "proceed":
        action = "proceed_with_caution"
        proceed = True
        reason = f"likely_blocked={noul} >= {thr} but safer_path=proceed; caution log"
    else:
        action = "proceed"
        proceed = True
        reason = f"likely_blocked={noul} < {thr}; safer_path={safer}"
    return {
        "action": action,
        "proceed": proceed,
        "reason": reason,
        "likely_blocked": noul,
        "safer_path": safer,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
