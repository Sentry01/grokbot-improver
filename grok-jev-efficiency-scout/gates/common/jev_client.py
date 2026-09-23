"""Thin Jev (TypeSafe System One) HTTP client.

POST https://api.typesafe.ai/v1/systemone with model jev-latest.
Auth: Bearer from os.environ["TYPESAFE_API_KEY"] — never printed or logged.
Fails soft: returns a structured error dict; does not raise/crash.
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
DEFAULT_TIMEOUT_S = 60

log = logging.getLogger("gates.jev_client")


def _mask_secrets(text: str) -> str:
    """Best-effort: strip any accidental key substring from error text."""
    key = os.environ.get("TYPESAFE_API_KEY") or ""
    if key and key in text:
        return text.replace(key, "***REDACTED***")
    return text


def call_jev(
    state: Any,
    questions: dict,
    *,
    model: str = MODEL,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    """Call Jev and return a normalized result dict.

    Success shape:
      {
        "ok": True,
        "http_status": 200,
        "latency_ms": float,
        "error": None,
        "model": str,
        "answers": dict,
        "usage": dict,
        "raw": dict,           # full API body
        "request_sans_auth": {"model", "state", "questions"},
      }

    Error shape (fail soft):
      {
        "ok": False,
        "http_status": int | None,
        "latency_ms": float,
        "error": str,
        "model": None,
        "answers": {},
        "usage": {},
        "raw": None | dict,
        "request_sans_auth": {...},
      }
    """
    request_sans_auth = {
        "model": model,
        "state": state,
        "questions": questions,
    }

    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        msg = "TYPESAFE_API_KEY not set in environment"
        log.error(msg)
        return {
            "ok": False,
            "http_status": None,
            "latency_ms": 0.0,
            "error": msg,
            "model": None,
            "answers": {},
            "usage": {},
            "raw": None,
            "request_sans_auth": request_sans_auth,
        }

    body = json.dumps(request_sans_auth).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Cloudflare blocks urllib's default UA (Error 1010 browser_signature_banned).
            "User-Agent": "GrokJevGates/1.0 (+https://api.typesafe.ai; Python)",
        },
        method="POST",
    )

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw_bytes = resp.read()
            http_status = getattr(resp, "status", 200) or 200
            headers = {k.lower(): v for k, v in resp.headers.items()}
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        try:
            data = json.loads(raw_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            msg = f"Jev response was not JSON: {e}"
            log.error(msg)
            return {
                "ok": False,
                "http_status": http_status,
                "latency_ms": latency_ms,
                "error": msg,
                "model": None,
                "answers": {},
                "usage": {},
                "raw": None,
                "request_sans_auth": request_sans_auth,
                "headers": headers,
            }
        return {
            "ok": True,
            "http_status": http_status,
            "latency_ms": latency_ms,
            "error": None,
            "model": data.get("model"),
            "answers": data.get("answers") or {},
            "usage": data.get("usage") or {},
            "raw": data,
            "request_sans_auth": request_sans_auth,
            "headers": {"content-type": headers.get("content-type")},
        }
    except urllib.error.HTTPError as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = ""
        err_body = _mask_secrets(err_body)[:500]
        msg = f"HTTP {e.code}: {_mask_secrets(str(e.reason))}"
        if err_body:
            msg = f"{msg} | body={err_body}"
        log.error("Jev API error: %s", msg)
        raw = None
        try:
            raw = json.loads(err_body) if err_body else None
        except json.JSONDecodeError:
            raw = {"body_text": err_body} if err_body else None
        return {
            "ok": False,
            "http_status": e.code,
            "latency_ms": latency_ms,
            "error": msg,
            "model": None,
            "answers": {},
            "usage": {},
            "raw": raw,
            "request_sans_auth": request_sans_auth,
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        msg = _mask_secrets(f"{type(e).__name__}: {e}")
        log.error("Jev client failure: %s", msg)
        return {
            "ok": False,
            "http_status": None,
            "latency_ms": latency_ms,
            "error": msg,
            "model": None,
            "answers": {},
            "usage": {},
            "raw": None,
            "request_sans_auth": request_sans_auth,
        }
