# core/tone_engine.py

class ToneEngine:
    """
    Simple tone selector based on mode and mood.
    """

    def select_tone(self, mode_name: str, mood: str) -> str:
        if mode_name == "AIMode":
            if mood == "neutral":
                return "conversational"
            elif mood == "positive":
                return "warm"
            elif mood == "stressed":
                return "reassuring"
            else:
                return "conversational"

        if mode_name == "F1Mode":
            if mood == "neutral":
                return "technical"
            elif mood == "stressed":
                return "calm-technical"
            else:
                return "technical"

        if mode_name == "F1EngineerMode":
            if mood == "neutral":
                return "tactical"
            elif mood == "stressed":
                return "urgent"
            else:
                return "tactical"

        return "neutral"
