#!/usr/bin/env python3
"""parallel-fanout gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("fan_out_noul_min", 0.6))
    noul = (answers.get("fan_out_ok") or {}).get("noul")
    bucket = (answers.get("max_parallel_bucket") or {}).get("score")
    # Map score → suggested concurrency cap
    cap_map = {0: 1, 1: 2, 2: 5, 3: 8}
    cap = 1
    if bucket is not None:
        # continuous score: floor to nearest legend index for cap hint
        idx = max(0, min(3, int(round(float(bucket)))))
        # if score is continuous average, use floor
        idx = max(0, min(3, int(float(bucket))))
        cap = cap_map.get(idx, 1)
        if float(bucket) >= 2.5:
            cap = 8
        elif float(bucket) >= 1.5:
            cap = 5
        elif float(bucket) >= 0.5:
            cap = 2
        else:
            cap = 1
    if noul is None:
        return {
            "action": "sequential",
            "proceed": False,
            "reason": "missing fan_out_ok; fail-open sequential",
            "fan_out_noul": None,
            "max_parallel_score": bucket,
            "max_parallel": 1,
            "threshold": thr,
        }
    parallel = float(noul) >= thr and cap > 1
    return {
        "action": "parallel" if parallel else "sequential",
        "proceed": parallel,
        "reason": (
            f"parallel: fan_out_ok={noul} >= {thr}; max_parallel≈{cap} (score={bucket})"
            if parallel
            else f"sequential: fan_out_ok={noul} (min {thr}) or cap={cap} (score={bucket})"
        ),
        "fan_out_noul": noul,
        "max_parallel_score": bucket,
        "max_parallel": cap if parallel else 1,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
