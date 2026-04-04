# core/context.py

class EngineerLine:
    """
    A single line Saul can say in Engineer Mode.
    """
    def __init__(self, text, requires_confirmation=False, on_confirm=None, on_confirm_action=None):
        self.text = text
        self.requires_confirmation = requires_confirmation
        self.on_confirm = on_confirm
        self.on_confirm_action = on_confirm_action


class Context:
    """
    Shared state for Saul's AI system.
    Holds session info, race info, and engineer-mode state.
    """

    def __init__(self):
        # Session info
        self.session_type = None
        self.track = None
        self.flag_state = None
        self.mood = "neutral"

        # Engineer-mode confirmation system
        self.awaiting_confirmation = False
        self.confirmation_response = None
        self.pending_action = None

        # Engineer-mode line queue (Saul's proactive radio messages)
        self.engineer_queue = []

    def update(self):
        """
        Future: update context from telemetry, session state, etc.
        """
        pass

    # ---------------------------------------------------------
    # Engineer Mode Helpers
    # ---------------------------------------------------------

    def request_confirmation(self, response_text, on_confirm_action=None):
        """
        Called when Saul asks the driver to confirm something.
        """
        self.awaiting_confirmation = True
        self.confirmation_response = response_text
        self.pending_action = on_confirm_action

    def clear_confirmation(self):
        """
        Clears confirmation state after the driver confirms.
        """
        self.awaiting_confirmation = False
        self.confirmation_response = None
        self.pending_action = None

    def queue_engineer_line(self, line: EngineerLine):
        """
        Add a proactive engineer line to the queue.
        """
        self.engineer_queue.append(line)

    def get_engineer_line(self):
        """
        Returns the next engineer line, if any.
        """
        if self.engineer_queue:
            return self.engineer_queue.pop(0)
        return None

