#!/usr/bin/env python3
"""routine-skill-schedule gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("worth_scheduling_min", 0.7))
    noul = (answers.get("worth_scheduling") or {}).get("noul")
    cadence = (answers.get("cadence") or {}).get("choice")
    if noul is None:
        return {
            "action": "do_not_schedule",
            "proceed": False,
            "reason": "missing worth_scheduling; fail-closed do_not_schedule",
            "worth_scheduling": None,
            "cadence": cadence,
            "threshold": thr,
        }
    schedule = float(noul) >= thr and cadence not in (None, "do_not_schedule")
    return {
        "action": cadence if schedule else "do_not_schedule",
        "proceed": schedule,
        "reason": (
            f"schedule: worth_scheduling={noul} >= {thr}; cadence={cadence}"
            if schedule
            else f"do_not_schedule: worth_scheduling={noul} (min {thr}) cadence={cadence}"
        ),
        "worth_scheduling": noul,
        "cadence": cadence,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
