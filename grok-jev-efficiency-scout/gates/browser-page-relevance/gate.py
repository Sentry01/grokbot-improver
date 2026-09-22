#!/usr/bin/env python3
"""browser-page-relevance gate — thin wrapper around shared runner."""
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
    thr = float((config.get("thresholds") or {}).get("page_worth_min", 0.6))
    noul = (answers.get("page_worth_deep_read") or {}).get("noul")
    nxt = (answers.get("next_browse_action") or {}).get("choice") or "extract_now"
    if noul is None:
        return {
            "action": "extract_now",
            "proceed": True,
            "reason": "missing page_worth_deep_read; fail-open continue once (extract_now)",
            "page_worth": None,
            "next_browse_action": nxt,
            "threshold": thr,
        }
    continue_browse = float(noul) >= thr and nxt in ("extract_now", "follow_one_link")
    # If low relevance, prefer next_browse_action (often back_to_search / stop_browse)
    if float(noul) < thr:
        action = nxt if nxt in ("back_to_search", "stop_browse", "follow_one_link") else "back_to_search"
        return {
            "action": action,
            "proceed": action == "follow_one_link",
            "reason": f"page_worth={noul} < {thr}; next={action}",
            "page_worth": noul,
            "next_browse_action": nxt,
            "threshold": thr,
        }
    return {
        "action": nxt,
        "proceed": continue_browse,
        "reason": f"page_worth={noul} >= {thr}; next_browse_action={nxt}",
        "page_worth": noul,
        "next_browse_action": nxt,
        "threshold": thr,
    }


def decide(state: dict) -> dict:
    """Importable: decide(state) -> outcome dict (includes decision + answers)."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
