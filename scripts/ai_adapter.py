#!/usr/bin/env python3
"""Provider-neutral AI API adapter for pipeline stage execution.

The adapter takes a runner-produced request JSON (versioned prompt + contract
+ inputs) and returns a response JSON in the same shape `run_pipeline.py
accept` consumes. Provider credentials live in scripts/ai_providers.json
(git-ignored; see scripts/ai_providers.example.json); keys themselves are
read from environment variables named in that config.

Red line: the adapter never decides rights. The caller (run_pipeline
run-stage) refuses external calls whenever the stage's external_processing
is not "allowed"; this module has no path around that gate.

Every call is logged to data/adapter_logs/calls.jsonl (git-ignored) with
prompt version, model, token usage, estimated cost, retry count, and latency.
Failures are logged too and surfaced, never swallowed.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
import os
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "scripts" / "ai_providers.json"
DEFAULT_LOG_DIR = ROOT / "data" / "adapter_logs"

DEFAULT_RETRY = {"max_attempts": 3, "base_delay_seconds": 1.0, "max_delay_seconds": 30.0}
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
REQUEST_TIMEOUT_SECONDS = 180


class AdapterError(Exception):
    """Non-retryable adapter failure (bad config, 4xx response, bad JSON)."""


class HttpStatusError(AdapterError):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:500]}")
        self.status = status
        self.body = body


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise SystemExit(
            f"provider config not found: {path} "
            "(copy scripts/ai_providers.example.json and fill in your settings)"
        )
    config = json.loads(path.read_text(encoding="utf-8"))
    if "providers" not in config:
        raise SystemExit(f"provider config missing 'providers': {path}")
    config.setdefault("retry", dict(DEFAULT_RETRY))
    return config


def resolve_api_key(provider: str, provider_config: dict[str, Any]) -> str:
    env_name = provider_config.get("api_key_env", "")
    key = os.environ.get(env_name, "")
    if not key:
        raise SystemExit(f"API key for provider '{provider}' not set in environment variable {env_name}")
    return key


def build_prompt_payload(request: dict[str, Any]) -> tuple[str, str]:
    """System + user text from a runner request JSON."""
    system = (
        request["prompt"]
        + "\n\nThe response must be a single JSON object matching this contract:\n"
        + json.dumps(request["contract"], ensure_ascii=False, indent=2)
    )
    user = json.dumps(request["inputs"], ensure_ascii=False, indent=2)
    return system, user


def http_post_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    http_request = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    try:
        with urllib.request.urlopen(http_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise HttpStatusError(exc.code, exc.read().decode("utf-8", errors="replace")) from exc


def _call_openai_compatible(cfg: dict[str, Any], api_key: str, system: str, user: str) -> dict[str, Any]:
    result = http_post_json(
        cfg["endpoint"],
        {"Authorization": f"Bearer {api_key}"},
        {
            "model": cfg["model"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        },
    )
    usage = result.get("usage", {})
    return {
        "content": result["choices"][0]["message"]["content"],
        "model": result.get("model", cfg["model"]),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
    }


def _call_anthropic(cfg: dict[str, Any], api_key: str, system: str, user: str) -> dict[str, Any]:
    result = http_post_json(
        cfg["endpoint"],
        {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        {
            "model": cfg["model"],
            "max_tokens": cfg.get("max_tokens", 8192),
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
    )
    usage = result.get("usage", {})
    return {
        "content": result["content"][0]["text"],
        "model": result.get("model", cfg["model"]),
        "prompt_tokens": usage.get("input_tokens", 0),
        "completion_tokens": usage.get("output_tokens", 0),
    }


def _call_google(cfg: dict[str, Any], api_key: str, system: str, user: str) -> dict[str, Any]:
    url = cfg["endpoint"].format(model=cfg["model"]) + f"?key={api_key}"
    result = http_post_json(
        url,
        {},
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
        },
    )
    usage = result.get("usageMetadata", {})
    return {
        "content": result["candidates"][0]["content"]["parts"][0]["text"],
        "model": cfg["model"],
        "prompt_tokens": usage.get("promptTokenCount", 0),
        "completion_tokens": usage.get("candidatesTokenCount", 0),
    }


PROVIDER_CALLS: dict[str, Callable[..., dict[str, Any]]] = {
    "openai": _call_openai_compatible,
    "kimi": _call_openai_compatible,
    "anthropic": _call_anthropic,
    "google": _call_google,
}


def estimate_cost(cfg: dict[str, Any], prompt_tokens: int, completion_tokens: int) -> float:
    return round(
        prompt_tokens / 1000 * cfg.get("cost_per_1k_input", 0.0)
        + completion_tokens / 1000 * cfg.get("cost_per_1k_output", 0.0),
        6,
    )


def parse_response_json(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AdapterError(f"model output is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AdapterError("model output is not a JSON object")
    return value


def log_call(record: dict[str, Any], log_dir: Path | str = DEFAULT_LOG_DIR) -> None:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    with (path / "calls.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def call_with_retry(
    provider: str,
    request: dict[str, Any],
    config_path: Path | str = DEFAULT_CONFIG_PATH,
    log_dir: Path | str = DEFAULT_LOG_DIR,
    log_context: dict[str, Any] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Call a provider with exponential backoff. Returns response + summary.

    Retries on network errors and retryable HTTP statuses (429/5xx); any
    other failure is final. The last failure is logged and re-raised.
    """
    config = load_config(config_path)
    providers = config["providers"]
    if provider not in providers:
        raise SystemExit(f"unknown provider '{provider}'; configured: {sorted(providers)}")
    cfg = providers[provider]
    if cfg.get("enabled", True) is False:
        raise SystemExit(f"provider '{provider}' is disabled in config")
    call = PROVIDER_CALLS[cfg.get("api", provider)]
    retry = {**DEFAULT_RETRY, **config.get("retry", {})}
    api_key = resolve_api_key(provider, cfg)
    system, user = build_prompt_payload(request)

    started = time.monotonic()
    attempts = 0
    last_error: Exception | None = None
    while attempts < retry["max_attempts"]:
        attempts += 1
        try:
            result = call(cfg, api_key, system, user)
            response = parse_response_json(result["content"])
            latency_ms = int((time.monotonic() - started) * 1000)
            cost = estimate_cost(cfg, result["prompt_tokens"], result["completion_tokens"])
            summary = {
                "provider": provider,
                "model": result["model"],
                "prompt_tokens": result["prompt_tokens"],
                "completion_tokens": result["completion_tokens"],
                "estimated_cost_usd": cost,
                "attempts": attempts,
                "latency_ms": latency_ms,
            }
            log_call({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "ok",
                "prompt_version": request.get("prompt_version", ""),
                "stage": request.get("stage", ""),
                **(log_context or {}),
                **summary,
            }, log_dir)
            return {"response": response, "model": f"{provider}:{result['model']}", "summary": summary}
        except HttpStatusError as exc:
            last_error = exc
            if exc.status not in RETRYABLE_STATUS:
                break
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        if attempts < retry["max_attempts"]:
            delay = min(retry["base_delay_seconds"] * 2 ** (attempts - 1), retry["max_delay_seconds"])
            sleep(delay)

    latency_ms = int((time.monotonic() - started) * 1000)
    log_call({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "error",
        "prompt_version": request.get("prompt_version", ""),
        "stage": request.get("stage", ""),
        **(log_context or {}),
        "provider": provider,
        "model": cfg.get("model", ""),
        "attempts": attempts,
        "latency_ms": latency_ms,
        "error": str(last_error)[:500] if last_error else "unknown",
    }, log_dir)
    raise SystemExit(f"adapter call failed after {attempts} attempt(s): {last_error}")

