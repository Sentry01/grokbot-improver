#!/usr/bin/env python3
"""memory-save gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("should_save_min", 0.7))
    noul = (answers.get("should_save") or {}).get("noul")
    kind = (answers.get("memory_kind") or {}).get("choice")
    if noul is None:
        return {
            "action": "skip_save",
            "proceed": False,
            "reason": "missing should_save; fail-open skip_save",
            "should_save": None,
            "memory_kind": kind,
            "threshold": thr,
        }
    if kind == "secret":
        return {
            "action": "refuse_store",
            "proceed": False,
            "reason": f"memory_kind=secret; must not store (should_save={noul})",
            "should_save": noul,
            "memory_kind": kind,
            "threshold": thr,
        }
    if kind == "ephemeral":
        return {
            "action": "skip_save",
            "proceed": False,
            "reason": f"memory_kind=ephemeral; skip durable save (should_save={noul})",
            "should_save": noul,
            "memory_kind": kind,
            "threshold": thr,
        }
    save = float(noul) >= thr
    return {
        "action": "save" if save else "skip_save",
        "proceed": save,
        "reason": (
            f"save: should_save={noul} >= {thr}; kind={kind}"
            if save
            else f"skip_save: should_save={noul} < {thr}; kind={kind}"
        ),
        "should_save": noul,
        "memory_kind": kind,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
