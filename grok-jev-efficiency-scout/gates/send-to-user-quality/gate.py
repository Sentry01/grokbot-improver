#!/usr/bin/env python3
"""send-to-user-quality gate — thin wrapper around shared runner."""
from __future__ import annotations

import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
ROOT = GATE_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.runner import decide as _decide  # noqa: E402
from common.runner import run_cli  # noqa: E402

EXTERNAL_CHANNELS = {"sendtouser", "email", "slack", "x_post", "webhook"}


def evaluate(answers: dict, config: dict, client_result: dict) -> dict:
    thr = config.get("thresholds") or {}
    ready_min = float(thr.get("ready_to_send_min", 0.7))
    quality_min = float(thr.get("send_quality_min", 2.0))

    ready = (answers.get("ready_to_send") or {}).get("noul")
    quality = (answers.get("send_quality") or {}).get("score")
    defect = (answers.get("main_defect") or {}).get("choice")

    if ready is None or quality is None:
        return {
            "action": "hold_send",
            "proceed": False,
            "reason": "missing ready_to_send or send_quality; fail-closed hold",
            "ready_to_send": ready,
            "send_quality": quality,
            "main_defect": defect,
            "thresholds": {"ready_to_send_min": ready_min, "send_quality_min": quality_min},
        }

    send = float(ready) >= ready_min and float(quality) >= quality_min
    return {
        "action": "send" if send else "revise",
        "proceed": send,
        "reason": (
            f"ready_to_send={ready}>={ready_min} AND send_quality={quality}>={quality_min}"
            if send
            else f"not ready: ready_to_send={ready} (min {ready_min}), send_quality={quality} (min {quality_min}), defect={defect}"
        ),
        "ready_to_send": ready,
        "send_quality": quality,
        "main_defect": defect,
        "thresholds": {"ready_to_send_min": ready_min, "send_quality_min": quality_min},
    }


def decide(state: dict) -> dict:
    """Importable decide(state). Fail-closed for external channels on API error via config."""
    return _decide(GATE_DIR, state, evaluate, write_dry=False)


if __name__ == "__main__":
    raise SystemExit(run_cli(GATE_DIR, evaluate))
