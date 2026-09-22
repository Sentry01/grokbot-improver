"""Shared gate runner: load config + state, call Jev, apply evaluate(), write dry/.

Each gate directory contains:
  config.json, example_state.json, gate.py (evaluate + decide), dry/
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional
from zoneinfo import ZoneInfo

from . import jev_client

SYD = ZoneInfo("Australia/Sydney")
log = logging.getLogger("gates.runner")

EvaluateFn = Callable[[dict, dict, dict], dict]
# evaluate(answers, config, client_result) -> decision dict
# decision must include at least: "action" (str), "proceed" (bool), "reason" (str)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_config(gate_dir: Path) -> dict:
    return load_json(gate_dir / "config.json")


def load_example_state(gate_dir: Path) -> Any:
    return load_json(gate_dir / "example_state.json")


def _fail_open_decision(config: dict, error: str) -> dict:
    default = config.get("default_on_error") or {}
    action = default.get("action", "continue")
    proceed = bool(default.get("proceed", True))
    return {
        "action": action,
        "proceed": proceed,
        "reason": f"fail-open on API error: {error}",
        "fail_mode_applied": "open",
        "api_error": error,
    }


def _fail_closed_decision(config: dict, error: str) -> dict:
    default = config.get("default_on_error") or {}
    action = default.get("action", "block")
    proceed = bool(default.get("proceed", False))
    return {
        "action": action,
        "proceed": proceed,
        "reason": f"fail-closed on API error: {error}",
        "fail_mode_applied": "closed",
        "api_error": error,
    }


def decide(
    gate_dir: Path | str,
    state: Any,
    evaluate: EvaluateFn,
    *,
    write_dry: bool = False,
    dry_name: Optional[str] = None,
) -> dict:
    """Call Jev with gate config questions + state; return decision outcome.

    Return shape:
      {
        "slug", "name", "ok", "http_status", "latency_ms", "error",
        "model", "answers", "usage",
        "decision": {...},
        "request_sans_auth": {...},
        "dry_path": str | None,
      }
    """
    gate_dir = Path(gate_dir).resolve()
    config = load_config(gate_dir)
    slug = config.get("slug") or gate_dir.name
    name = config.get("name") or slug
    questions = config["questions"]
    fail_mode = (config.get("fail_mode") or "open").lower()

    client_result = jev_client.call_jev(state, questions)

    if not client_result.get("ok"):
        err = client_result.get("error") or "unknown API error"
        if fail_mode == "closed":
            decision = _fail_closed_decision(config, err)
        else:
            decision = _fail_open_decision(config, err)
    else:
        try:
            decision = evaluate(
                client_result.get("answers") or {},
                config,
                client_result,
            )
        except Exception as e:
            log.exception("evaluate() raised for slug=%s", slug)
            err = f"evaluate_error: {type(e).__name__}: {e}"
            if fail_mode == "closed":
                decision = _fail_closed_decision(config, err)
            else:
                decision = _fail_open_decision(config, err)

    outcome = {
        "slug": slug,
        "name": name,
        "ok": bool(client_result.get("ok")),
        "http_status": client_result.get("http_status"),
        "latency_ms": client_result.get("latency_ms"),
        "error": client_result.get("error"),
        "model": client_result.get("model"),
        "answers": client_result.get("answers") or {},
        "usage": client_result.get("usage") or {},
        "decision": decision,
        "request_sans_auth": client_result.get("request_sans_auth"),
        "as_of": datetime.now(SYD).strftime("%Y-%m-%d %H:%M:%S AEST"),
        "dry_path": None,
    }

    if write_dry:
        dry_path = write_dry_result(gate_dir, outcome, client_result, dry_name=dry_name)
        outcome["dry_path"] = str(dry_path)

    return outcome


def write_dry_result(
    gate_dir: Path,
    outcome: dict,
    client_result: dict,
    *,
    dry_name: Optional[str] = None,
) -> Path:
    """Write one dry-call JSON under gate_dir/dry/ (auth never included)."""
    slug = outcome.get("slug") or gate_dir.name
    fname = dry_name or f"dry_{slug.replace('-', '_')}.json"
    path = gate_dir / "dry" / fname
    payload = {
        "meta": {
            "name": fname.replace(".json", ""),
            "slug": slug,
            "http_status": outcome.get("http_status"),
            "latency_ms": outcome.get("latency_ms"),
            "error": outcome.get("error"),
            "as_of": outcome.get("as_of"),
            "headers": client_result.get("headers") or {},
        },
        "request_sans_auth": outcome.get("request_sans_auth"),
        "response": {
            "model": outcome.get("model"),
            "answers": outcome.get("answers"),
            "usage": outcome.get("usage"),
        }
        if outcome.get("ok")
        else (client_result.get("raw") or {"error": outcome.get("error")}),
        "decision": outcome.get("decision"),
    }
    write_json(path, payload)
    log.info("wrote dry result %s (http=%s latency_ms=%s)", path, outcome.get("http_status"), outcome.get("latency_ms"))
    return path


def run_cli(gate_dir: Path | str, evaluate: EvaluateFn) -> int:
    """`python gate.py` entry: dry-run with example_state.json, exit 0 always (fail soft)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    gate_dir = Path(gate_dir).resolve()
    state = load_example_state(gate_dir)
    outcome = decide(gate_dir, state, evaluate, write_dry=True)

    # Human-readable one-liner to stderr (no secrets)
    d = outcome.get("decision") or {}
    print(
        f"[{outcome.get('slug')}] http={outcome.get('http_status')} "
        f"latency_ms={outcome.get('latency_ms')} ok={outcome.get('ok')} "
        f"action={d.get('action')} proceed={d.get('proceed')} "
        f"dry={outcome.get('dry_path')}",
        file=sys.stderr,
    )
    # Machine-readable summary on stdout
    summary = {
        "slug": outcome.get("slug"),
        "http_status": outcome.get("http_status"),
        "latency_ms": outcome.get("latency_ms"),
        "ok": outcome.get("ok"),
        "error": outcome.get("error"),
        "answers": outcome.get("answers"),
        "decision": outcome.get("decision"),
        "dry_path": outcome.get("dry_path"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0  # fail soft: always exit 0 so harnesses don't crash
