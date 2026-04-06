# core/llm_client.py
# Ollama LLM client with streaming and persistent text cache.

import os
import hashlib
import threading
import time
from typing import Iterator


class LLMClient:
    """
    Ollama client with streaming output and persistent text cache.
    Pre-warms model at startup to eliminate cold-start delay.
    Caches responses by prompt hash for instant replay.
    """

    BASE_URL = "http://localhost:11434"
    CACHE_DIR = "assets/voices/cache/llm"

    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model
        self._prewarmed = False
        self._prewarm_done = threading.Event()

        os.makedirs(self.CACHE_DIR, exist_ok=True)

    # ---------------------------------------------------------
    # Pre-warm
    # ---------------------------------------------------------

    def prewarm(self):
        """Load model into memory. Run once at startup."""
        if self._prewarmed:
            return

        def _prewarm():
            try:
                import requests
                r = requests.post(
                    f"{self.BASE_URL}/api/generate",
                    json={"model": self.model, "prompt": "OK", "stream": False},
                    timeout=120,
                )
                if r.status_code == 200:
                    self._prewarmed = True
                    print("[LLM] Model pre-warmed")
                else:
                    print(f"[LLM] Pre-warm failed: {r.status_code}")
            except Exception as e:
                print(f"[LLM] Pre-warm error: {e}")
            finally:
                self._prewarm_done.set()

        t = threading.Thread(target=_prewarm, daemon=True)
        t.start()

    @property
    def is_ready(self) -> bool:
        return self._prewarmed

    # ---------------------------------------------------------
    # Cache
    # ---------------------------------------------------------

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.CACHE_DIR, f"{key}.txt")

    def _prompt_key(self, system: str, prompt: str) -> str:
        data = f"{self.model}:{system}:{prompt}".encode()
        return hashlib.sha256(data).hexdigest()[:24]

    def _cached_get(self, key: str) -> str | None:
        path = self._cache_path(key)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def _cached_set(self, key: str, text: str):
        path = self._cache_path(key)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    # ---------------------------------------------------------
    # Generate
    # ---------------------------------------------------------

    def generate(self, prompt: str, *, system: str = "") -> Iterator[str]:
        """
        Stream tokens from Ollama. Yields tokens as they arrive.
        After streaming completes, returns full response.
        """
        import requests

        full = []
        params = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": True,
        }

        try:
            with requests.post(
                f"{self.BASE_URL}/api/generate",
                json=params,
                stream=True,
                timeout=120,
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        import json
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            full.append(token)
                            yield token
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception as e:
            yield f"[LLM error: {e}]"

    def cached_generate(self, prompt: str, *, system: str = "") -> str:
        """
        Check cache first. If miss, stream from Ollama, cache result.
        Returns full response text.
        """
        key = self._prompt_key(system, prompt)
        cached = self._cached_get(key)
        if cached is not None:
            return cached

        full = []
        for token in self.generate(prompt, system=system):
            full.append(token)

        result = "".join(full)
        self.cache_store(system, prompt, result)
        return result

    def cache_store(self, system: str, prompt: str, response: str):
        """Store a response in the cache."""
        key = self._prompt_key(system, prompt)
        self._cached_set(key, response)
