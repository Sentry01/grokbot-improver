#!/usr/bin/env python3
"""redundant-tool-call gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("is_redundant_min", 0.65))
    noul = (answers.get("is_redundant") or {}).get("noul")
    strat = (answers.get("reuse_strategy") or {}).get("choice")
    if noul is None:
        return {
            "action": "allow_call",
            "proceed": True,
            "reason": "missing is_redundant; fail-open allow_call",
            "is_redundant": None,
            "reuse_strategy": strat,
            "threshold": thr,
        }
    redundant = float(noul) >= thr and strat != "not_redundant"
    if redundant:
        action = strat if strat in ("reuse_cache", "narrow_delta", "different_source") else "reuse_cache"
        return {
            "action": action,
            "proceed": action in ("narrow_delta", "different_source"),
            "reason": f"redundant noul={noul} >= {thr}; strategy={action}",
            "is_redundant": noul,
            "reuse_strategy": strat,
            "threshold": thr,
        }
    return {
        "action": "allow_call",
        "proceed": True,
        "reason": f"not redundant: is_redundant={noul} (min {thr}); strategy={strat}",
        "is_redundant": noul,
        "reuse_strategy": strat,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
