#!/usr/bin/env python3
"""search-fetch-triage gate — thin wrapper around shared runner."""
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
    thr = config.get("thresholds") or {}
    keep_min = float(thr.get("keep_noul_min", 0.55))
    util_min = float(thr.get("utility_score_min", 1.5))
    keep_noul = (answers.get("keep") or {}).get("noul")
    utility = (answers.get("utility") or {}).get("score")
    if keep_noul is None and utility is None:
        return {
            "action": "keep",
            "proceed": True,
            "reason": "missing answers; fail-open keep (top-N harness)",
            "keep_noul": None,
            "utility": None,
            "thresholds": {"keep_noul_min": keep_min, "utility_score_min": util_min},
        }
    keep = (keep_noul is not None and float(keep_noul) >= keep_min) or (
        utility is not None and float(utility) >= util_min
    )
    return {
        "action": "keep" if keep else "drop",
        "proceed": keep,
        "reason": (
            f"keep: keep_noul={keep_noul} (min {keep_min}) OR utility={utility} (min {util_min})"
            if keep
            else f"drop: keep_noul={keep_noul} < {keep_min} AND utility={utility} < {util_min}"
        ),
        "keep_noul": keep_noul,
        "utility": utility,
        "thresholds": {"keep_noul_min": keep_min, "utility_score_min": util_min},
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
