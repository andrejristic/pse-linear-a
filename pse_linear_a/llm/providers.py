"""LLM binding — one interface, 4 backends: Claude / Mistral / Groq (API) + local GGUF
(LM Studio OpenAI-compatible). stdlib-only HTTP (urllib). Fails GRACEFULLY: when a
provider is unavailable, complete() returns None so callers use a template fallback.

Model IDs are configurable. Defaults use current-generation Claude ids; confirm/adjust
in config as needed.
"""
from __future__ import annotations
import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path

from .. import constants as K

CONFIG_PATH = Path.home() / ".config" / "pse-linear-a" / "config.json"

DEFAULT_MODELS = {
    "claude": "claude-opus-4-8",
    "mistral": "mistral-large-latest",
    "groq": "llama-3.3-70b-versatile",
    "local_gguf": "local-model",
}


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception:
        return {}


def _key(provider: str, cfg: dict) -> str | None:
    env = {"claude": "ANTHROPIC_API_KEY", "mistral": "MISTRAL_API_KEY",
           "groq": "GROQ_API_KEY"}.get(provider)
    return (cfg.get("keys", {}).get(provider)) or (os.environ.get(env) if env else None)


@dataclass
class LLMProvider:
    name: str
    model: str
    api_key: str | None = None
    base_url: str | None = None
    timeout: float = 30.0

    @property
    def available(self) -> bool:
        if self.name == "local_gguf":
            return True   # attempt localhost; complete() degrades if server is down
        return bool(self.api_key)

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str | None:
        try:
            if self.name == "claude":
                return self._anthropic(system, user, max_tokens)
            return self._openai_compatible(system, user, max_tokens)
        except Exception:
            return None

    # --- Anthropic Messages API ---
    def _anthropic(self, system, user, max_tokens):
        body = json.dumps({
            "model": self.model, "max_tokens": max_tokens, "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=body,
            headers={"content-type": "application/json", "x-api-key": self.api_key,
                     "anthropic-version": "2023-06-01"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = json.load(r)
        return "".join(b.get("text", "") for b in data.get("content", []))

    # --- OpenAI-compatible (mistral / groq / local LM Studio) ---
    def _openai_compatible(self, system, user, max_tokens):
        base = self.base_url or {
            "mistral": "https://api.mistral.ai/v1",
            "groq": "https://api.groq.com/openai/v1",
            "local_gguf": K.LOCAL_GGUF_BASE_URL,
        }[self.name]
        body = json.dumps({
            "model": self.model, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
        }).encode()
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(f"{base}/chat/completions", data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = json.load(r)
        return data["choices"][0]["message"]["content"]


def get_provider(name: str = "local_gguf") -> LLMProvider:
    cfg = _load_config()
    models = {**DEFAULT_MODELS, **cfg.get("models", {})}
    return LLMProvider(name=name, model=models.get(name, DEFAULT_MODELS[name]),
                       api_key=_key(name, cfg))


def available_providers() -> dict[str, bool]:
    return {p: get_provider(p).available for p in K.PROVIDERS}
