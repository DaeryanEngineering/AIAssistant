# core/keyboard_listener.py

import threading
from typing import Callable, Optional


class KeyboardListener:
    """
    Global keyboard listener for pit confirmation.
    Listens for Insert key press regardless of which window is focused.
    """

    def __init__(self, on_insert: Optional[Callable] = None):
        self.on_insert = on_insert
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._keyboard = None

    def start(self):
        """Start the global keyboard listener."""
        if self._running:
            return

        try:
            import keyboard
            self._keyboard = keyboard
            keyboard.hook_key("insert", self._on_insert_pressed)
            self._running = True
            print("[KeyboardListener] Listening for Insert key")
        except ImportError:
            print("[KeyboardListener] 'keyboard' package not installed. Install with: pip install keyboard")
        except PermissionError:
            print("[KeyboardListener] Permission denied. Run as administrator for global key capture.")

    def _on_insert_pressed(self, event):
        """Called when Insert key is pressed."""
        if event.event_type == "down" and self.on_insert:
            self.on_insert()

    def stop(self):
        """Stop the keyboard listener."""
        if self._keyboard and self._running:
            self._keyboard.unhook_all()
            self._running = False
            print("[KeyboardListener] Stopped")
