#!/usr/bin/env python3
"""Append one gate decision to decisions.jsonl. Usage: python log_decision.py '<json object>'"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parent / "logs" / "decisions.jsonl"

def main() -> None:
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    obj = json.loads(raw)
    obj.setdefault("ts", datetime.now(timezone.utc).astimezone().isoformat())
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print("logged", obj.get("gate"), obj.get("action"))

if __name__ == "__main__":
    main()
