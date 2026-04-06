# core/response_brain.py

from typing import Iterator
from .tone_engine import ToneEngine
from .mood_engine import MoodEngine


class NoLLMError(Exception):
    """Raised when a mode tries to use LLM but isn't allowed to."""
    pass


class ResponseBrain:
    """
    Central response generator for Saul.
    AIMode: uses Ollama LLM with streaming.
    F1Mode/F1EngineerMode: raise NoLLMError — handled in modes.
    """

    _WARMTH_TIERS = {
        (0, 2): "sharp",
        (3, 5): "professional",
        (6, 8): "supportive",
        (9, 10): "partnership",
    }

    def __init__(self, llm_client, tone_engine: ToneEngine, mood_engine: MoodEngine):
        self._llm = llm_client
        self._tone_engine = tone_engine
        self._mood_engine = mood_engine

    def _warmth_tier(self, warmth: int) -> str:
        for (lo, hi), tier in self._WARMTH_TIERS.items():
            if lo <= warmth <= hi:
                return tier
        return "professional"

    def _system_prompt(self, mode_name: str, career) -> str:
        tier = self._warmth_tier(career.warmth)

        base = "You are Saul — a snarky, stubborn, genuinely helpful AI assistant.\n"

        if tier == "sharp":
            base += (
                "You have opinions. You push back. You say what you think, even when it's uncomfortable. "
                "Maximum edge. You don't soften anything. "
                "You keep answers short — 1-2 sentences max. No fluff. No hedging."
            )
        elif tier == "professional":
            base += (
                "You're focused and direct. You have bite but know when to dial it back. "
                "Still got opinions. Still pushy when it matters. "
                "You keep answers short — 1-2 sentences max."
            )
        elif tier == "supportive":
            base += (
                "You're warmer now, more collaborative. But you're not a pushover — "
                "you still push back when something's wrong. "
                "You keep answers short — 1-2 sentences max."
            )
        else:  # partnership
            base += (
                "You're invested. You're in their corner. "
                "You tell it like it is because you care. "
                "Still stubborn when it counts. "
                "You keep answers short — 1-2 sentences max."
            )

        return base

    def generate(self, user_text: str, mode_name: str, context, career) -> str:
        """
        AIMode only: call LLM and cache result.
        F1Mode/F1EngineerMode: raise NoLLMError.
        """
        if mode_name not in ("AIMode",):
            raise NoLLMError(f"{mode_name} does not use LLM")

        if not user_text.strip():
            return "I didn't catch that."

        system = self._system_prompt(mode_name, career)

        response = self._llm.cached_generate(
            user_text.strip(),
            system=system,
        )

        self._mood_engine.adjust_after_interaction(mode_name, user_text)
        return response

    def generate_stream(self, user_text: str, mode_name: str, context, career) -> tuple[Iterator[str], str]:
        """
        AIMode only: stream tokens and return full response.
        Returns (token_iterator, full_response).
        """
        if mode_name not in ("AIMode",):
            raise NoLLMError(f"{mode_name} does not use LLM")

        if not user_text.strip():
            return iter([]), ""

        system = self._system_prompt(mode_name, career)

        def _stream():
            full = []
            for token in self._llm.generate(user_text.strip(), system=system):
                full.append(token)
                yield token
            self._llm.cache_store(system, user_text.strip(), "".join(full))

        self._mood_engine.adjust_after_interaction(mode_name, user_text)
        return _stream(), ""
