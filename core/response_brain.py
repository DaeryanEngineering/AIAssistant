# core/response_brain.py

from .tone_engine import ToneEngine
from .mood_engine import MoodEngine

class ResponseBrain:
    """
    Central response generator for Saul.
    """

    def __init__(self, tone_engine: ToneEngine, mood_engine: MoodEngine):
        self._tone_engine = tone_engine
        self._mood_engine = mood_engine

    def generate(self, user_text: str, mode_name: str, context) -> str:
        mood = self._mood_engine.get_mood()
        tone = self._tone_engine.select_tone(mode_name, mood)

        base = user_text.strip() or "I didn't catch that."

        response = f"[{mode_name} | mood={mood} | tone={tone}] {base}"
        self._mood_engine.adjust_after_interaction(mode_name, user_text)
        return response
