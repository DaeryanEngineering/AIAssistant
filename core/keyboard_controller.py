import time
import threading
import keyboard


class KeyboardController:
    """
    Keyboard simulation wrapper for F1 25 input.
    Uses pydirectinput for game-compatible key presses.
    All key presses use HOLD instead of press() for reliability.
    """

    KEYS = {
        "drs": "f9",
        "ers_overtake": "f10",
        "ers_cycle_left": "f11",
        "ers_cycle_right": "f8",
        "mfd_up": "num8",
        "mfd_down": "num2",
        "mfd_left": "num4",
        "mfd_right": "num6",
        "mfd_confirm": "enter",
        "mfd_open": "num0",
    }

    PRESS_DELAY = 0.15
    HOLD_DURATION = 0.12

    def __init__(self):
        self._current_ers_mode = None  # Sync with telemetry on first use
        self._lock = threading.Lock()
        self._pydirectinput = None
        self._initialized = False
        self._confirm_callback = None

        # Start keyboard listener thread for Insert key
        threading.Thread(target=self._keyboard_listener, daemon=True).start()

    def _keyboard_listener(self):
        """Listen for Insert key for confirm."""
        try:
            # Use correct keyboard API
            keyboard.on_press_key('insert', self._on_insert_key)
        except Exception as e:
            print(f"[Keyboard] Failed to register Insert key listener: {e}")

    def _on_insert_key(self):
        """Handle Insert key press."""
        if self._confirm_callback:
            self._confirm_callback()

    def register_confirm_callback(self, callback):
        """Register callback for Insert key press."""
        self._confirm_callback = callback

    def _init(self):
        if not self._initialized:
            import pydirectinput
            self._pydirectinput = pydirectinput
            self._pydirectinput.FAILSAFE = False
            self._initialized = True

    # ----------------------------------------------------------------------
    # LOW-LEVEL INPUT
    # ----------------------------------------------------------------------

    def _hold(self, key, duration=None):
        """Hold a key long enough for F1 25 to register it."""
        self._init()
        dur = duration or self.HOLD_DURATION

        self._pydirectinput.keyDown(key)
        time.sleep(dur)
        self._pydirectinput.keyUp(key)
        time.sleep(self.PRESS_DELAY)

    # ----------------------------------------------------------------------
    # DRS
    # ----------------------------------------------------------------------

    def press_drs(self):
        """Activate DRS via F9."""
        with self._lock:
            print("[KEYBOARD] DRS pressed")
            self._hold(self.KEYS["drs"])

    # ----------------------------------------------------------------------
    # ERS
    # ----------------------------------------------------------------------

    def sync_ers_mode(self, mode_from_telemetry):
        """Call once per update loop to sync with real game mode."""
        if self._current_ers_mode is None:
            self._current_ers_mode = mode_from_telemetry

    def press_ers_overtake(self):
        """Activate ERS Overtake mode via F10."""
        with self._lock:
            print("[KEYBOARD] ERS Overtake pressed")
            self._hold(self.KEYS["ers_overtake"])
            self._current_ers_mode = 3

    def cycle_ers_to(self, target_mode):
        """
        Cycle ERS mode using D-Pad Left/Right.
        Modes: 0=None, 1=Medium, 2=Hotlap, 3=Overtake
        """
        with self._lock:
            if self._current_ers_mode is None:
                self._current_ers_mode = 1

            current = self._current_ers_mode
            if current == target_mode:
                return

            diff = (target_mode - current) % 4
            direction = "right" if diff <= 2 else "left"
            print(f"[KEYBOARD] ERS cycling from {current} to {target_mode} via {direction}")

            if diff <= 2:
                for _ in range(diff):
                    self._hold(self.KEYS["ers_cycle_right"])
            else:
                for _ in range(4 - diff):
                    self._hold(self.KEYS["ers_cycle_left"])

            self._current_ers_mode = target_mode

    # ----------------------------------------------------------------------
    # MFD NAVIGATION
    # ----------------------------------------------------------------------

    def open_mfd(self):
        with self._lock:
            self._hold(self.KEYS["mfd_open"])

    def mfd_up(self):
        with self._lock:
            self._hold(self.KEYS["mfd_up"])

    def mfd_down(self):
        with self._lock:
            self._hold(self.KEYS["mfd_down"])

    def mfd_left(self):
        with self._lock:
            self._hold(self.KEYS["mfd_left"])

    def mfd_right(self):
        with self._lock:
            self._hold(self.KEYS["mfd_right"])

    def mfd_confirm(self):
        with self._lock:
            self._hold(self.KEYS["mfd_confirm"])

    def navigate_to_compound(self, target_compound_index):
        with self._lock:
            for _ in range(target_compound_index):
                self._hold(self.KEYS["mfd_right"])

    def select_pit_compound(self, target_compound_index, prefer_new=True):
        with self._lock:
            self._hold(self.KEYS["mfd_open"])
            time.sleep(0.3)

            for _ in range(3):
                self._hold(self.KEYS["mfd_down"])
            time.sleep(0.3)

            self.navigate_to_compound(target_compound_index)
            time.sleep(0.2)

            self._hold(self.KEYS["mfd_confirm"])

    @property
    def current_ers_mode(self):
        return self._current_ers_mode

    def stop_ers(self):
        """Cycle ERS to None (mode 0)."""
        with self._lock:
            while self._current_ers_mode != 0:
                self._hold(self.KEYS["ers_cycle_left"])
                self._current_ers_mode = (self._current_ers_mode - 1) % 4
