# core/context.py

class Context:
    """
    Shared state for Saul's AI system.
    """

    def __init__(self):
        self.session_type = None
        self.track = None
        self.flag_state = None
        self.mood = "neutral"

    def update(self):
        """Future: update context from telemetry, voice, etc."""
        pass
