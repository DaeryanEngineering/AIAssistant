# core/input_manager.py

class InputManager:
    """
    Simple push-to-talk (PTT) state tracker.
    """

    def __init__(self):
        self._current = False
        self._previous = False

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
