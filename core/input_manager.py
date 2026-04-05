# core/input_manager.py

class InputManager:
    """
    Tracks PTT state AND provides a simple text buffer
    for AIMode and F1Mode.
    """

    def __init__(self):
        # PTT state
        self._current = False
        self._previous = False

        # NEW: text input buffer
        self._text_buffer = None

    # ---------------------------------------------------------
    # PTT handling
    # ---------------------------------------------------------
    def set_ptt_state(self, pressed: bool) -> None:
        """Set the current PTT button state (True = held, False = not held)."""
        self._previous = self._current
        self._current = pressed

    def is_pressed(self) -> bool:
        """Returns True on the frame PTT transitions from False -> True."""
        return self._current and not self._previous

    def is_released(self) -> bool:
        """Returns True on the frame PTT transitions from True -> False."""
        return not self._current and self._previous

    def is_held(self) -> bool:
        """Returns True while PTT is held down."""
        return self._current

    # ---------------------------------------------------------
    # NEW: Text input handling
    # ---------------------------------------------------------
    def submit_text(self, text: str):
        """
        Called by your UI (or test harness) to deliver a line of text to Saul.
        """
        self._text_buffer = text

    def has_text(self):
        return self._text_buffer is not None

    def consume_text(self):
        if self._text_buffer:
            text = self._text_buffer
            self._text_buffer = None
            return text
        return None

    def get_text(self):
        """
        AIMode and F1Mode call this once per update.
        Returns the text and clears the buffer.
        """
        if self._text_buffer:
            text = self._text_buffer
            self._text_buffer = None
            return text
        return None
