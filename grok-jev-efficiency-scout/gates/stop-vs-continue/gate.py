#!/usr/bin/env python3
"""stop-vs-continue gate — thin wrapper around shared runner."""
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
    stop_min = float(thr.get("should_stop_min", 0.6))
    mv_min = float(thr.get("marginal_value_min", 1.5))

    should_stop = (answers.get("should_stop") or {}).get("noul")
    mv = (answers.get("marginal_value_of_next_call") or {}).get("score")

    stop_by_noul = should_stop is not None and float(should_stop) >= stop_min
    stop_by_mv = mv is not None and float(mv) < mv_min
    stop = bool(stop_by_noul or stop_by_mv)

    if should_stop is None and mv is None:
        return {
            "action": "continue",
            "proceed": True,
            "reason": "missing answers; fail-open continue once",
            "should_stop": should_stop,
            "marginal_value": mv,
            "thresholds": {"should_stop_min": stop_min, "marginal_value_min": mv_min},
        }

    return {
        "action": "stop" if stop else "continue",
        "proceed": not stop,  # proceed=True means continue the loop
        "reason": (
            f"stop: should_stop={should_stop} (min {stop_min}) OR marginal_value={mv} (min {mv_min})"
            if stop
            else f"continue: should_stop={should_stop} < {stop_min} AND marginal_value={mv} >= {mv_min}"
        ),
        "should_stop": should_stop,
        "marginal_value": mv,
        "stop_by_noul": stop_by_noul,
        "stop_by_mv": stop_by_mv,
        "thresholds": {"should_stop_min": stop_min, "marginal_value_min": mv_min},
    }


def decide(state: dict) -> dict:
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
